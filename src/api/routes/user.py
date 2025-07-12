"""User routes for user management and authentication."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List

from src.models.profiles import ProfileInDb, ProfilePublic
from src.api.dependencies.auth import get_current_user
from src.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.models.token import AccessToken
from src.db.repos.user import UserRepository
from src.models.user import UserLogin, UserPublic, UserUpdate, UserMe
from src.api.dependencies.database import get_repository
from src.errors.database import NotFoundError
from src.db.repos.user_profile import UserProfileRepository
from src.models.user_profile import UserProfileCreate, UserProfilePublic, UserProfileCreateResponse

user_router = APIRouter()


@user_router.post(
    "/create-user",
    response_model=UserProfileCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_profile_create: UserProfileCreate,
    user_profile_repo: UserProfileRepository = Depends(get_repository(UserProfileRepository)),
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserProfileCreateResponse:
    """Create a new user with profile and return user_id, pin, and profile_id."""
    user_profile_in_db = await user_profile_repo.create_user_profile(
        new_user=user_profile_create.user,
        new_profile=user_profile_create.profile,
    )
    return UserProfileCreateResponse(
        user_id=user_profile_in_db.user.user_id,
        pin=user_profile_create.user.pin,  # Return the plain PIN from request
        profile_id=str(user_profile_in_db.profile.profile_id)
    )


@user_router.get(
    "/get-users",
    response_model=List[UserPublic],
    status_code=status.HTTP_200_OK,
)
async def get_users(
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> List[UserPublic]:
    """Get all active users."""
    users_in_db = await user_repo.get_users()
    return [UserPublic(**user.dict()) for user in users_in_db]


@user_router.get(
    "/get-user-by-id/{user_id}",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(
    user_id: str,
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserPublic:
    """Get a user by their ID."""
    try:
        user_in_db = await user_repo.get_user_by_id(user_id=user_id)
        return UserPublic(**user_in_db.dict())
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user_router.put(
    "/update-user/{user_id}",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserPublic:
    """Update an existing user's information."""
    try:
        return await user_repo.update_user(user_id=user_id, user_update=user_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user_router.delete(
    "/delete-user/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    user_id: str,
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> dict:
    """Soft delete a user."""
    try:
        await user_repo.delete_user(user_id=user_id)
        return {"message": "User successfully deleted."}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user_router.post(
    "/login",
    response_model=AccessToken,
    status_code=status.HTTP_200_OK,
)
async def user_login(
    response: Response,
    login_data: UserLogin,
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> AccessToken:
    """Authenticate user and return access token with HTTP-only cookie."""
    token = await user_repo.login(login_data)

    # Set HTTP-only cookie for client-side authentication
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
    """Logout user and clear authentication cookie."""
    response.delete_cookie("access_token")
    return {"message": "Logged out."}


@user_router.get("/me", response_model=UserMe, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: ProfileInDb = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
) -> UserMe:
    """Get current user's ID and PIN hash."""
    try:
        # Get the full user data including PIN from the database
        user_in_db = await user_repo.get_user_by_id(user_id=str(current_user.user_id))
        return UserMe(user_id=user_in_db.user_id, pin_hash=user_in_db.pin_hash)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
