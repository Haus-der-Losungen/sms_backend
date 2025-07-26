"""User Profile repository for combined user and profile operations."""

import logging
from databases import Database

from src.models.profiles import ProfileCreate
from src.models.user import UserCreate
from src.models.user_profile import UserProfileInDb
from src.db.repos.base import BaseRepository
from src.db.repos.profiles import ProfileRepository
from src.db.repos.user import UserRepository
from src.utils.helpers import Helpers

audit_logger = logging.getLogger("audit")


class UserProfileRepository(BaseRepository):
    """Repository for combined user and profile operations."""

    def __init__(self, db: Database) -> None:
        """Initialize the repository with database connection."""
        super().__init__(db)
        self.user_repo = UserRepository(db)
        self.profile_repo = ProfileRepository(db)

    async def create_user_profile(
        self,
        *,
        new_user: UserCreate,
        new_profile: ProfileCreate,
    ) -> tuple[UserProfileInDb, str]:
        """Create a new user and profile in a single transaction."""
        async with self.db.transaction():
            # Create user first
            user, generated_pin = await self.user_repo.create_user(new_user=new_user)
            audit_logger.info(f"Created user: {user.user_id}")
            print(f"Received PIN from user creation: {generated_pin}")  # Debug log

            # Create profile with user_id
            profile_data = new_profile.model_copy(
                update={"user_id": user.user_id}
            )

            profile = await self.profile_repo.create_profile(new_profile=profile_data)
            audit_logger.info(f"Created profile: {profile.profile_id}")
            print(f"Returning PIN from user_profile: {generated_pin}")  # Debug log
            
            return UserProfileInDb(user=user, profile=profile), generated_pin

    async def get_user_profiles_by_role(self, *, role: str, search: str = None) -> list[UserProfileInDb]:
        """Get user profiles by role, with optional search on profile fields."""
        users = await self.user_repo.get_users_by_role(role=role, search=search)
        profiles = []
        for user in users:
            try:
                profile = await self.profile_repo.get_profile_by_user_id(user_id=user.user_id)
                profiles.append(UserProfileInDb(user=user, profile=profile))
            except Exception:
                continue
        return profiles

