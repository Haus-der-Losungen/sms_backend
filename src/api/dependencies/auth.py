"""Dependency for user auth"""

from databases import Database
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from src.api.dependencies.database import get_database
from src.db.repos.user import UserRepository
from src.services.auth import AuthService
from src.models.user import UserInDb

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_auth_service() -> AuthService:
    """Auth Service Dependency."""
    return AuthService()


async def get_user_repository(db: Database = Depends(get_database)) -> UserRepository:
    """User Repository Dependency."""
    return UserRepository(db)


async def get_token_from_cookies(request: Request) -> str:
    """Get the access token from cookies."""
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
) -> UserInDb:
    """Get the current user from the access token."""
    try:
        user_id = await auth_service.verify_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    user = await user_repo.get_user_by_id(user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return user
