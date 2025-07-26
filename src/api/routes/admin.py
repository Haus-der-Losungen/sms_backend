"""Admin and school management routes."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from src.api.dependencies.auth import require_admin
from src.api.dependencies.database import get_repository
from src.db.repos.user_profile import UserProfileRepository
from src.models.user_profile import UserProfileCreate, UserProfilePublic
from src.models.user import UserUpdate

admin_router = APIRouter()

@admin_router.get("/profile", response_model=UserProfilePublic, status_code=status.HTTP_200_OK)
async def get_admin_profile(
    current_user_data = Depends(require_admin),
):
    """Fetch the current admin's profile."""
    user, profile = current_user_data
    return UserProfilePublic(user=user, profile=profile)

@admin_router.post("/students", response_model=UserProfilePublic, status_code=status.HTTP_201_CREATED)
async def create_student(
    user_profile_create: UserProfileCreate,
    user_profile_repo: UserProfileRepository = Depends(get_repository(UserProfileRepository)),
    current_user_data = Depends(require_admin),
):
    """Create a new student (admin only)."""
    # Force role to student
    user_profile_create.user.role = "student"
    user_profile_in_db, _ = await user_profile_repo.create_user_profile(
        new_user=user_profile_create.user,
        new_profile=user_profile_create.profile,
    )
    return UserProfilePublic(user=user_profile_in_db.user, profile=user_profile_in_db.profile)

@admin_router.get("/students", response_model=List[UserProfilePublic], status_code=status.HTTP_200_OK)
async def list_students(
    search: Optional[str] = Query(None, description="Search by name or email"),
    user_profile_repo: UserProfileRepository = Depends(get_repository(UserProfileRepository)),
    current_user_data = Depends(require_admin),
):
    """List/search students (admin only)."""
    students = await user_profile_repo.get_user_profiles_by_role(role="student", search=search)
    return [UserProfilePublic(user=s.user, profile=s.profile) for s in students]

@admin_router.get("/staff", response_model=List[UserProfilePublic], status_code=status.HTTP_200_OK)
async def list_staff(
    search: Optional[str] = Query(None, description="Search by name or email"),
    user_profile_repo: UserProfileRepository = Depends(get_repository(UserProfileRepository)),
    current_user_data = Depends(require_admin),
):
    """List/search staff (admin only)."""
    staff = await user_profile_repo.get_user_profiles_by_role(role="staff", search=search)
    return [UserProfilePublic(user=s.user, profile=s.profile) for s in staff]

@admin_router.put("/students/{user_id}", response_model=UserProfilePublic, status_code=status.HTTP_200_OK)
async def update_student(
    user_id: str,
    user_update: UserUpdate,
    user_profile_repo: UserProfileRepository = Depends(get_repository(UserProfileRepository)),
    current_user_data = Depends(require_admin),
):
    """Update a student (admin only)."""
    # Only allow updating role to student
    user_update.role = "student"
    user = await user_profile_repo.user_repo.update_user(user_id=user_id, user_update=user_update)
    profile = await user_profile_repo.profile_repo.get_profile_by_user_id(user_id=user_id)
    return UserProfilePublic(user=user, profile=profile)

@admin_router.delete("/students/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_student(
    user_id: str,
    user_profile_repo: UserProfileRepository = Depends(get_repository(UserProfileRepository)),
    current_user_data = Depends(require_admin),
):
    """Delete a student (admin only)."""
    await user_profile_repo.user_repo.delete_user(user_id=user_id)
    return {"message": "Student deleted successfully."} 