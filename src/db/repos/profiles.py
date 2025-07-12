"""Profile repository for database operations."""

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
  profile_id, user_id, first_name, last_name, phone, gender, email
)
VALUES (
  :profile_id, :user_id, :first_name, :last_name, :phone, :gender, :email
)
RETURNING *
"""

GET_PROFILES_QUERY = """
SELECT * FROM profiles
WHERE is_deleted = FALSE
"""

GET_PROFILE_BY_ID_QUERY = """
SELECT * FROM profiles
WHERE profile_id = :profile_id AND is_deleted = FALSE
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
WHERE profile_id = :profile_id AND is_deleted = FALSE
RETURNING *
"""

DELETE_PROFILE_QUERY = """
UPDATE profiles
SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE profile_id = :profile_id AND is_deleted = FALSE
RETURNING *
"""

audit_logger = logging.getLogger("audit")


class ProfileRepository(BaseRepository):
    """Repository for profile database operations."""

    def __init__(self, db: Database) -> None:
        """Initialize the repository with database connection."""
        super().__init__(db)

    async def create_profile(self, *, new_profile: ProfileCreate) -> ProfileInDb:
        """Create a new profile in the database."""
        try:
            profile_id = str(uuid.uuid4())
            audit_logger.info(f"Creating profile for email: {new_profile.email}")

            # Extract user_id if it was added by the service layer
            user_id = getattr(new_profile, 'user_id', None)
            if not user_id:
                raise ValueError("user_id is required for profile creation")

            values = {
                "profile_id": profile_id,
                "user_id": user_id,
                "first_name": new_profile.first_name,
                "last_name": new_profile.last_name,
                "phone": new_profile.phone,
                "gender": new_profile.gender,
                "email": new_profile.email.lower() if new_profile.email else None,
            }

            created = await self.db.fetch_one(query=CREATE_PROFILE_QUERY, values=values)
            if not created:
                audit_logger.error("Failed to create profile in database.")
                raise Exception("Failed to create profile in database.")
            
            audit_logger.info(f"Profile created successfully with ID: {profile_id}")
            return ProfileInDb(**dict(created))

        except ValidationError as e:
            audit_logger.error(f"Validation error creating profile: {e}")
            raise
        except Exception as e:
            audit_logger.error(f"Error creating profile: {e}")
            raise

    async def get_profile_by_id(self, *, id: uuid.UUID) -> ProfileInDb:
        """Get a profile by its ID."""
        profile = await self.db.fetch_one(query=GET_PROFILE_BY_ID_QUERY, values={"profile_id": str(id)})
        if not profile:
            raise NotFoundError(entity_name="Profile", entity_identifier=str(id))
        return ProfileInDb(**dict(profile))

    async def get_profile_by_email(self, *, email: str) -> ProfileInDb:
        """Get a profile by email address."""
        profile = await self.db.fetch_one(query=GET_PROFILE_BY_EMAIL_QUERY, values={"email": email.lower()})
        if not profile:
            raise NotFoundError(entity_name="Profile", entity_identifier=email)
        return ProfileInDb(**dict(profile))

    async def get_profile_by_user_id(self, *, user_id: int) -> ProfileInDb:
        """Get a profile by user ID."""
        profile = await self.db.fetch_one(query=GET_PROFILE_BY_USER_ID_QUERY, values={"user_id": user_id})
        if not profile:
            raise NotFoundError(entity_name="Profile", entity_identifier=str(user_id))
        return ProfileInDb(**dict(profile))
        
    async def update_profile(self, *, id: uuid.UUID, profile_update: ProfileUpdate) -> ProfileInDb:
        """Update an existing profile's information."""
        try:
            values = {
                "profile_id": str(id),
                **profile_update.model_dump(exclude_unset=True),
            }

            updated = await self.db.fetch_one(query=UPDATE_PROFILE_QUERY, values=values)

            if not updated:
                raise NotFoundError(entity_name="Profile", entity_identifier=str(id))

            audit_logger.info(f"Profile with ID: {id} updated successfully")
            return ProfileInDb(**dict(updated))

        except ValidationError as e:
            audit_logger.error(f"Validation error updating profile: {e}")
            raise
        except Exception as e:
            audit_logger.error(f"Error updating profile {id}: {e}")
            raise

    async def delete_profile(self, *, id: uuid.UUID) -> ProfileInDb:
        """Soft delete a profile."""
        try:
            deleted = await self.db.fetch_one(query=DELETE_PROFILE_QUERY, values={"profile_id": str(id)})

            if not deleted:
                raise NotFoundError(entity_name="Profile", entity_identifier=str(id))

            audit_logger.info(f"Profile with ID: {id} deleted successfully")
            return ProfileInDb(**dict(deleted))

        except Exception as e:
            audit_logger.error(f"Error deleting profile {id}: {e}")
            raise

    async def get_profiles(self) -> List[ProfileInDb]:
        """Get all active profiles."""
        profiles = await self.db.fetch_all(query=GET_PROFILES_QUERY)
        return [ProfileInDb(**dict(profile)) for profile in profiles]
