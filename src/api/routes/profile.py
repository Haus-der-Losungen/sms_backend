"""Profile routes."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.database import get_repository
from src.db.repos.profiles import ProfileRepository
from src.models.profiles import ProfilePublic, ProfileUpdate, ProfileCreate
from src.models.user_profile import UserProfileInDb

profile_router = APIRouter()


@profile_router.get(
    "",
    response_model=List[ProfilePublic],
    status_code=status.HTTP_200_OK,
)
async def get_profiles(
    profile_repo: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> List[ProfilePublic]:
    """Get all profiles."""
    profiles_in_db = await profile_repo.get_profiles()
    return [ProfilePublic(**profile.dict()) for profile in profiles_in_db]


@profile_router.get(
    "/search",
    response_model=ProfilePublic,
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    profile_repo: ProfileRepository = Depends(get_repository(ProfileRepository)),
    profile_id: Optional[UUID] = Query(default=None, description="The profile's UUID"),
    user_id: Optional[int] = Query(default=None, description="The associated user's ID"),
) -> ProfilePublic:
    """Get a profile by profile ID or user ID."""
    if profile_id is None and user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either profile_id or user_id must be provided.",
        )
    if profile_id is not None:
        profile = await profile_repo.get_profile_by_id(id=profile_id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found.",
            )
        return profile
    if user_id is not None:
        profile = await profile_repo.get_profile_by_user_id(user_id=user_id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found.",
            )
        return profile
        return await profile_repo.get_profile_by_user_id(user_id=user_id)
@profile_router.get(
    "/me",
    response_model=ProfilePublic,
    status_code=status.HTTP_200_OK,
)
async def get_current_user_profile(
    current_user: UserProfileInDb = Depends(get_current_user),
) -> ProfilePublic:
    """Get the current user's profile details."""
    return current_user.profile


@profile_router.post(
    "",
    response_model=ProfilePublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    profile: ProfileCreate,
    profile_repo: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> ProfilePublic:
    """Create a new profile."""
    created = await profile_repo.create_profile(new_profile=profile)
    return ProfilePublic(**created.dict())


@profile_router.patch(
    "/{profile_id}",
    response_model=ProfilePublic,
    status_code=status.HTTP_200_OK,
)
async def update_profile(
    profile_id: UUID,
    profile_update: ProfileUpdate,
    profile_repo: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> ProfilePublic:
    """Update a profile by its ID."""
    return await profile_repo.update_profile(
        id=profile_id, profile_update=profile_update
    )


@profile_router.delete(
    "/{profile_id}",
    response_model=ProfilePublic,
    status_code=status.HTTP_200_OK,
)
async def delete_profile(
    profile_id: UUID,
    profile_repo: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> ProfilePublic:
    """Soft delete a profile by its ID."""
    return await profile_repo.delete_profile(id=profile_id)
