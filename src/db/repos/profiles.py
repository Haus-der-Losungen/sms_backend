"""Profile repository."""

import logging
from typing import List
import uuid

from databases import Database
from pydantic import ValidationError

from src.db.repos.base import BaseRepository
from src.errors.database import NotFoundError
from src.models.profiles import ProfileCreate, ProfileInDb, ProfileUpdate

# SQL Queries
CREATE_PROFILE_QUERY = """
INSERT INTO profiles (
    id, user_id, first_name, last_name, phone, gender, email, user_type
)
VALUES (
    :id, :user_id, :first_name, :last_name, :phone, :gender, :email, :user_type
)
RETURNING *
"""
GET_PROFILES_QUERY = """
SELECT * FROM profiles
WHERE is_deleted = FALSE
"""

GET_PROFILE_BY_ID_QUERY = """
SELECT * FROM profiles
WHERE id = :id AND is_deleted = FALSE
"""

GET_PROFILE_BY_EMAIL_QUERY = """
SELECT * FROM profiles
WHERE email = :email AND is_deleted = FALSE
"""

GET_PROFILE_BY_USER_ID_QUERY = """
SELECT * FROM profiles
WHERE user_id = :user_id AND is_deleted = FALSE
"""

UPDATE_PROFILE_QUERY = """
UPDATE profiles
SET 
    first_name = COALESCE(:first_name, first_name),
    last_name = COALESCE(:last_name, last_name),
    phone = COALESCE(:phone, phone),
    gender = COALESCE(:gender, gender),
    updated_at = CURRENT_TIMESTAMP
WHERE id = :id AND is_deleted = FALSE
RETURNING *
"""

DELETE_PROFILE_QUERY = """
UPDATE profiles
SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE id = :id AND is_deleted = FALSE
RETURNING *
"""

audit_logger = logging.getLogger("audit")


class ProfileRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)

    async def create_profile(self, *, new_profile: ProfileCreate) -> ProfileInDb:
        try:
            profile_id = str(uuid.uuid4())
            audit_logger.info(f"Creating profile for email: {new_profile.email}")

            values = {
                "id": profile_id,
                "user_id": str(new_profile.user_id) if new_profile.user_id else None,
                "first_name": new_profile.first_name,
                "last_name": new_profile.last_name,
                "phone": new_profile.phone,
                "gender": new_profile.gender,
                "email": new_profile.email.lower() if new_profile.email else None,
                "user_type": new_profile.user_type,
            }

            created = await self.db.fetch_one(query=CREATE_PROFILE_QUERY, values=values)
            audit_logger.info(f"Profile created successfully with ID: {profile_id}")
            return ProfileInDb(**created)

        except ValidationError as e:
            audit_logger.error(f"Validation error creating profile: {e}")
            raise

        except Exception as e:
            audit_logger.error(f"Error creating profile: {e}")
            raise

    async def get_profile_by_id(self, *, id: uuid.UUID) -> ProfileInDb:
        profile = await self.db.fetch_one(query=GET_PROFILE_BY_ID_QUERY, values={"id": str(id)})
        if not profile:
            raise NotFoundError(entity_name="Profile", entity_identifier=str(id))
        return ProfileInDb(**profile)

    async def get_profile_by_email(self, *, email: str) -> ProfileInDb:
        profile = await self.db.fetch_one(query=GET_PROFILE_BY_EMAIL_QUERY, values={"email": email.lower()})
        if not profile:
            raise NotFoundError(entity_name="Profile", entity_identifier=email)
        return ProfileInDb(**profile)

    async def get_profile_by_user_id(self, *, user_id: uuid.UUID) -> ProfileInDb:
        profile = await self.db.fetch_one(query=GET_PROFILE_BY_USER_ID_QUERY, values={"user_id": str(user_id)})
        if not profile:
            raise NotFoundError(entity_name="Profile", entity_identifier=str(user_id))
        return ProfileInDb(**profile)

    async def update_profile(self, *, id: uuid.UUID, profile_update: ProfileUpdate) -> ProfileInDb:
        try:
            values = {
                "id": str(id),
                **profile_update.model_dump(exclude_unset=True),
            }

            updated = await self.db.fetch_one(query=UPDATE_PROFILE_QUERY, values=values)

            if not updated:
                raise NotFoundError(entity_name="Profile", entity_identifier=str(id))

            audit_logger.info(f"Profile with ID: {id} updated successfully")
            return ProfileInDb(**updated)

        except ValidationError as e:
            audit_logger.error(f"Validation error updating profile: {e}")
            raise

        except Exception as e:
            audit_logger.error(f"Error updating profile {id}: {e}")
            raise

    async def delete_profile(self, *, id: uuid.UUID) -> ProfileInDb:
        try:
            deleted = await self.db.fetch_one(query=DELETE_PROFILE_QUERY, values={"id": str(id)})

            if not deleted:
                raise NotFoundError(entity_name="Profile", entity_identifier=str(id))

            audit_logger.info(f"Profile with ID: {id} deleted successfully")
            return ProfileInDb(**deleted)

        except Exception as e:
            audit_logger.error(f"Error deleting profile {id}: {e}")
            raise
    
    async def get_profiles(self) -> List[ProfileInDb]:
        """
        Retrieve all profiles.
        """
        profiles = await self.db.fetch_all(query=GET_PROFILES_QUERY)
        return [ProfileInDb(**profile) for profile in profiles]
