import logging
import uuid
from typing import List, Optional

from databases import Database

from pydantic import EmailStr, ValidationError

from src.models.token import AccessToken
from src.db.repos.base import BaseRepository
from src.errors.database import IncorrectCredentialsError, NotFoundError
from src.models.user import UserCreate, UserInDb, UserLogin, UserUpdate
from src.services.auth import AuthService

CREATE_USER_QUERY = """
INSERT INTO users (
    user_id, email, password_hash
)
VALUES (:user_id, :email, :password_hash)
RETURNING *
"""

GET_USERS_QUERY = """
SELECT * FROM users
WHERE is_deleted = FALSE
"""

GET_USER_BY_ID_QUERY = """
SELECT * FROM users 
WHERE user_id = :user_id AND is_deleted = FALSE
"""

GET_USER_BY_EMAIL_QUERY = """
SELECT * FROM users 
WHERE email = :email AND is_deleted = FALSE
"""

UPDATE_USER_QUERY = """
UPDATE users
SET email = COALESCE(:email, email),
    updated_at = CURRENT_TIMESTAMP
WHERE user_id = :user_id
RETURNING *
"""

DELETE_USER_QUERY = """
UPDATE users
SET is_deleted = TRUE,
    updated_at = CURRENT_TIMESTAMP
WHERE user_id = :user_id AND is_deleted = FALSE
RETURNING *
"""

audit_logger = logging.getLogger("audit")


class UserRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)

    async def create_user(self, *, new_user: UserCreate) -> UserInDb:
        try:
            user_id = str(uuid.uuid4())
            hashed_password = await AuthService().get_password_hash(new_user.password_hash)

            values = {
                "user_id": user_id,
                "email": new_user.email,
                "password_hash": hashed_password
            }

            audit_logger.info(f"Creating user, email: {new_user.email}")
            created_user = await self.db.fetch_one(query=CREATE_USER_QUERY, values=values)
            audit_logger.info(f"User created successfully, ID: {user_id}")
            return UserInDb(**created_user)
        except ValidationError as e:
            audit_logger.error(f"Validation error creating user: {e}")
            raise
        except Exception as e:
            audit_logger.error(f"Error creating user: {e}")
            raise

    async def get_user_by_id(self, *, user_id: uuid.UUID) -> UserInDb:
        user = await self.db.fetch_one(query=GET_USER_BY_ID_QUERY, values={"user_id": str(user_id)})
        if not user:
            raise NotFoundError(entity_name="User", entity_identifier=str(user_id))
        return UserInDb(**user)

    async def get_user_by_email(self, email: str) -> Optional[UserInDb]:
        user = await self.db.fetch_one(query=GET_USER_BY_EMAIL_QUERY, values={"email": email})
        return UserInDb(**user) if user else None

    async def get_users(self) -> List[UserInDb]:
        users = await self.db.fetch_all(query=GET_USERS_QUERY)
        return [UserInDb(**user) for user in users]

    async def update_user(self, *, user_id: uuid.UUID, user_update: UserUpdate) -> UserInDb:
        try:
            values = {"user_id": str(user_id)}
            if user_update.email:
                values["email"] = user_update.email
            updated_user = await self.db.fetch_one(query=UPDATE_USER_QUERY, values=values)
            if not updated_user:
                raise NotFoundError(entity_name="User", entity_identifier=str(user_id))
            audit_logger.info(f"User with ID: {user_id} updated successfully")
            return UserInDb(**updated_user)
        except ValidationError as e:
            audit_logger.error(f"Validation error updating user: {e}")
            raise
        except Exception as e:
            audit_logger.error(f"Error updating user {user_id}: {e}")
            raise

    async def delete_user(self, *, user_id: uuid.UUID) -> UserInDb:
        try:
            deleted_user = await self.db.fetch_one(query=DELETE_USER_QUERY, values={"user_id": str(user_id)})
            if not deleted_user:
                raise NotFoundError(entity_name="User", entity_identifier=str(user_id))
            audit_logger.info(f"User with ID: {user_id} deleted successfully")
            return UserInDb(**deleted_user)
        except Exception as e:
            audit_logger.error(f"Error deleting user {user_id}: {e}")
            raise

    async def login(self, login_data: UserLogin) -> AccessToken:
     email: EmailStr = login_data.email
     password: str = login_data.password 

     print("email: ", email)
     print("password: ", password)

     user = await self.get_user_by_email(email=email)

     if not user or not await AuthService().verify_password(password, user.password_hash):
        raise IncorrectCredentialsError()

     access_token = AuthService().create_access_token(
        data={"user_id": str(user.user_id)}
    )

     return AccessToken(
        access_token=access_token,
        token_type="bearer"
    )

