from fastapi import APIRouter, Depends, HTTPException, Response, status
from uuid import UUID
from typing import List

from src.models.profiles import ProfileInDb
from src.api.dependencies.auth import get_current_user
from src.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.models.token import AccessToken
from src.db.repos.user import UserRepository
from src.models.user import  UserLogin, UserPublic, UserUpdate
from src.api.dependencies.database import get_repository
from src.errors.database import NotFoundError
from src.db.repos.user_profile import UserProfileRepository
from src.models.user_profile import (UserProfileCreate, UserProfileInDb, UserProfilePublic,)

user_router = APIRouter()


@user_router.post(
    "/create-user",
    response_model=UserProfilePublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_profile_create: UserProfileCreate,
    user_profile_repo: UserProfileRepository = Depends(
        get_repository(UserProfileRepository)
    ),
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserProfilePublic:
    """Create a new user."""
    user = await user_repo.get_user_by_email(
        email=user_profile_create.user.email
    )
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )
    return await user_profile_repo.create_user_profile(
        new_user=user_profile_create.user,
        new_profile=user_profile_create.profile,
    )


@user_router.get(
    "/get-users",
    response_model=List[UserPublic],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> List[UserPublic]:
    """Get all users."""
    return await user_repo.get_users()


@user_router.get(
    "/get-user-by-id/{user_id}",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(
    user_id: UUID,
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserPublic:
    """Get a user by ID."""
    try:
        return await user_repo.get_user_by_id(user_id=user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user_router.put(
    "/update-user/{user_id}",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserPublic:
    """Update an existing user's details."""
    try:
        return await user_repo.update_user(user_id=user_id, user_update=user_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user_router.delete(
    "/delete-user/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: UUID,
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> dict:
    """Delete a user."""
    try:
        await user_repo.delete_user(user_id=user_id)
        return {"message": "User successfully deleted."}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@user_router.post("/login", response_model=AccessToken, status_code=status.HTTP_200_OK)
async def user_login(
    response: Response,
    login_data: UserLogin,
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> AccessToken:
    login_data.email = login_data.email.lower()

    token = await user_repo.login(login_data)

    response.set_cookie(
        "access_token",
        value=token.access_token,
        httponly=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return token

@user_router.post("/logout", response_model=dict, status_code=status.HTTP_200_OK)
async def user_logout(
    response: Response,
    user: ProfileInDb = Depends(get_current_user),
) -> dict:
    """Logout user."""
    response.delete_cookie("access_token")
    return {"message": "logged out."}


