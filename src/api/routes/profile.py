"""Profile routes."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies.auth import (
    get_current_user,
    
)
from src.api.dependencies.database import get_repository
from src.db.repos.profiles import ProfileRepository
from src.models.profiles import ProfilePublic, ProfileUpdate
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
    return await profile_repo.get_profiles()


@profile_router.get(
    "/search",
    response_model=ProfilePublic,
    status_code=status.HTTP_200_OK,
)
async def get_profile(
    profile_repo: ProfileRepository = Depends(get_repository(ProfileRepository)),
    profile_id: Optional[UUID] = Query(None, description="The profile's UUID"),
    user_id: Optional[UUID] = Query(None, description="The associated user's UUID"),
) -> ProfilePublic:
    """Get a profile by profile ID or user ID."""
    if not (profile_id or user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either profile_id or user_id must be provided.",
        )
    if profile_id:
        return await profile_repo.get_profile_by_id(id=profile_id)
    return await profile_repo.get_profile_by_user_id(user_id=user_id)


#@profile_router.get(
    "/me",
    response_model=ProfilePublic,
    status_code=status.HTTP_200_OK,
#)
#async def get_current_user_profile(
    current_user: UserProfileInDb = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_repository(ProfileRepository)),
#) -> ProfilePublic:
    """Get the current user's profile details."""
    return current_user.profile


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