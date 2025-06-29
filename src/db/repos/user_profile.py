"""User Profile repository."""

import logging
from databases import Database

from src.models.profiles import ProfileCreate
from src.models.user import UserCreate
from src.models.user_profile import UserProfileInDb
from src.db.repos.base import BaseRepository
from src.db.repos.profiles import ProfileRepository
from src.db.repos.user import UserRepository

audit_logger = logging.getLogger("audit")


class UserProfileRepository(BaseRepository):
    """User Profile repository."""

    def __init__(self, db: Database) -> None:
        """Initialize the repository."""
        super().__init__(db)
        self.user_repo = UserRepository(db)
        self.profile_repo = ProfileRepository(db)

    async def create_user_profile(
        self,
        *,
        new_user: UserCreate,
        new_profile: ProfileCreate,
    ) -> UserProfileInDb:
        """Create a new user and profile."""
        async with self.db.transaction():
            user = await self.user_repo.create_user(new_user=new_user)
            audit_logger.info(f"Created user: {user.email}")

            new_profile.user_id = user.user_id
            new_profile.email = user.email

            profile = await self.profile_repo.create_profile(new_profile=new_profile)
            audit_logger.info(f"Created profile: {profile.id} for user: {user.user_id}")

            return UserProfileInDb(user=user, profile=profile)
