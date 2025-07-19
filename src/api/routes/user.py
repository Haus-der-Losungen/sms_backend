"""User routes for user management and authentication."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List

from src.models.profiles import ProfileInDb, ProfilePublic
from src.api.dependencies.auth import get_current_user, get_current_user_with_role, require_admin, require_staff
from src.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from src.models.token import AccessToken
from src.db.repos.user import UserRepository
from src.models.user import UserLogin, UserPublic, UserUpdate, UserMe, UserMeWithRole
from src.api.dependencies.database import get_repository
from src.errors.database import NotFoundError
from src.db.repos.user_profile import UserProfileRepository
from src.models.user_profile import UserProfileCreate, UserProfilePublic, UserProfileCreateResponse
from src.models.user import UserInDb

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
    
    # Debug the incoming request
    print(f"Received user PIN: {user_profile_create.user.pin}")
    print(f"Type of received PIN: {type(user_profile_create.user.pin)}")
    print(f"Received PIN is None: {user_profile_create.user.pin is None}")
    
    user_profile_in_db, generated_pin = await user_profile_repo.create_user_profile(
        new_user=user_profile_create.user,
        new_profile=user_profile_create.profile,
    )
    
    print(f"Generated PIN in endpoint: {generated_pin}")  # Debug log
    print(f"Type of generated_pin: {type(generated_pin)}")  # Debug log
    print(f"Generated PIN repr: {repr(generated_pin)}")  # Debug log
    
    response_data = UserProfileCreateResponse(
        user_id=user_profile_in_db.user.user_id,
        pin=generated_pin,  # Return the generated PIN
        profile_id=str(user_profile_in_db.profile.profile_id)
    )
    
    print(f"Response data pin: {response_data.pin}")  # Debug log
    print(f"Response data type: {type(response_data.pin)}")  # Debug log
    
    return response_data



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
        updated_user = await user_repo.update_user(user_id=user_id, user_update=user_update)
        user_dict = updated_user.dict()
        user_dict.pop('pin_hash', None)  # Remove pin_hash field
        return UserPublic(**user_dict)
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


@user_router.get("/me", response_model=UserMeWithRole, status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user_data: tuple[UserInDb, ProfileInDb] = Depends(get_current_user_with_role),
) -> UserMeWithRole:
    """Get current user's ID, role, and profile information."""
    user, profile = current_user_data
    # Create profile dict excluding is_deleted field
    profile_dict = profile.dict()
    profile_dict.pop('is_deleted', None)  # Remove is_deleted field if present
    
    return UserMeWithRole(
        user_id=user.user_id,
        role=user.role,
        profile=ProfilePublic(**profile_dict)
    )


# Role-protected endpoints examples
@user_router.get(
    "/admin-only",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def admin_only_endpoint(
    current_user_data: tuple[UserInDb, ProfileInDb] = Depends(require_admin),
) -> dict:
    """Admin-only endpoint example."""
    user, profile = current_user_data
    return {
        "message": "Admin access granted",
        "user_id": user.user_id,
        "role": user.role,
        "user_name": f"{profile.first_name} {profile.last_name}"
    }


@user_router.get(
    "/staff-and-admin",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def staff_and_admin_endpoint(
    current_user_data: tuple[UserInDb, ProfileInDb] = Depends(require_staff),
) -> dict:
    """Staff and admin endpoint example."""
    user, profile = current_user_data
    return {
        "message": "Staff/Admin access granted",
        "user_id": user.user_id,
        "role": user.role,
        "user_name": f"{profile.first_name} {profile.last_name}"
    }
