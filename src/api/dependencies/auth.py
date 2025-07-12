"""Authentication dependencies for user authentication and authorization."""

from databases import Database
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from src.api.dependencies.database import get_database, get_repository
from src.db.repos.user import UserRepository
from src.db.repos.profiles import ProfileRepository
from src.services.auth import AuthService
from src.models.user import UserInDb
from src.models.profiles import ProfileInDb

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_auth_service() -> AuthService:
    """Get AuthService dependency."""
    return AuthService()


async def get_user_repository(db: Database = Depends(get_database)) -> UserRepository:
    """Get UserRepository dependency."""
    return UserRepository(db)


async def get_token_from_cookies(request: Request) -> str:
    """Extract access token from HTTP-only cookies."""
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. Token not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return access_token


async def get_current_user(
    token: str = Depends(get_token_from_cookies),
    auth_service: AuthService = Depends(get_auth_service),
    user_repo: UserRepository = Depends(get_user_repository),
    profile_repo: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> ProfileInDb:
    """Get the current user's profile from the access token."""
    try:
        # Verify token and extract user_id
        user_id = await auth_service.verify_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Get user from database
    user = await user_repo.get_user_by_id(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Get the user's profile
    profile = await profile_repo.get_profile_by_user_id(user_id=int(user.user_id))
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Profile not found",
        )

    return profile
