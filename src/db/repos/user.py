"""User repository for database operations."""

import logging
from typing import List

from databases import Database
from pydantic import ValidationError

from src.utils.helpers import Helpers
from src.models.token import AccessToken
from src.db.repos.base import BaseRepository
from src.errors.database import IncorrectCredentialsError, NotFoundError
from src.models.user import UserCreate, UserInDb, UserLogin, UserUpdate
from src.services.auth import AuthService

# SQL Queries
CREATE_USER_QUERY = """
INSERT INTO users (
    user_id, role, pin_hash
)
VALUES (:user_id, :role, :pin_hash)
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

UPDATE_USER_QUERY = """
UPDATE users
SET role = COALESCE(:role, role),
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
    """Repository for user database operations."""

    def __init__(self, db: Database) -> None:
        """Initialize the repository with database connection."""
        super().__init__(db)

    async def create_user(self, *, new_user: UserCreate) -> UserInDb:
        """Create a new user in the database."""
        try:
            # Generate sequential user ID
            user_id = Helpers.generate_sequential_id()
            
            # Hash the plain PIN
            pin_hash = await AuthService().get_pin_hash(new_user.pin)

            values = {
                "user_id": user_id,
                "role": new_user.role,
                "pin_hash": pin_hash
            }

            created_user = await self.db.fetch_one(query=CREATE_USER_QUERY, values=values)
            if not created_user:
                audit_logger.error("Failed to create user in database.")
                raise Exception("Failed to create user in database.")
            
            audit_logger.info(f"User created successfully, ID: {user_id}")
            return UserInDb(**dict(created_user))
            
        except ValidationError as e:
            audit_logger.error(f"Validation error creating user: {e}")
            raise
        except Exception as e:
            audit_logger.error(f"Error creating user: {e}")
            raise

    async def get_user_by_id(self, *, user_id: str) -> UserInDb:
        """Get a user by their ID."""
        user = await self.db.fetch_one(query=GET_USER_BY_ID_QUERY, values={"user_id": user_id})
        if not user:
            raise NotFoundError(entity_name="User", entity_identifier=user_id)
        return UserInDb(**dict(user))

    async def get_users(self) -> List[UserInDb]:
        """Get all active users."""
        users = await self.db.fetch_all(query=GET_USERS_QUERY)
        return [UserInDb(**dict(user)) for user in users]

    async def update_user(self, *, user_id: str, user_update: UserUpdate) -> UserInDb:
        """Update an existing user's information."""
        values = {
            "user_id": user_id,
            "role": user_update.role
        }
        updated_user = await self.db.fetch_one(query=UPDATE_USER_QUERY, values=values)
        if not updated_user:
            raise NotFoundError(entity_name="User", entity_identifier=user_id)
        
        audit_logger.info(f"User with ID: {user_id} updated successfully")
        return UserInDb(**dict(updated_user))

    async def delete_user(self, *, user_id: str) -> UserInDb:
        """Soft delete a user."""
        deleted_user = await self.db.fetch_one(query=DELETE_USER_QUERY, values={"user_id": user_id})
        if not deleted_user:
            raise NotFoundError(entity_name="User", entity_identifier=user_id)
        
        audit_logger.info(f"User with ID: {user_id} deleted successfully")
        return UserInDb(**dict(deleted_user))

    async def login(self, login_data: UserLogin) -> AccessToken:
        """Authenticate user and return access token."""
        try:
            plain_pin = login_data.pin
            user_id = login_data.user_id

            # Get user from database
            user = await self.get_user_by_id(user_id=user_id)
            
            # Verify PIN
            if not user or not await AuthService().verify_pin(plain_pin, user.pin_hash):
                raise IncorrectCredentialsError()

            # Create access token
            access_token = AuthService().create_access_token(
                data={"user_id": str(user.user_id)}
            )

            audit_logger.info(f"User login successful: {user_id}")
            return AccessToken(
                access_token=access_token,
                token_type="bearer"
            )
            
        except IncorrectCredentialsError:
            audit_logger.warning(f"Incorrect credentials for user ID: {login_data.user_id}")
            raise
        except Exception as e:
            audit_logger.error(f"Login error for user ID: {login_data.user_id} - {e}")
            raise
