"""Auth  module."""

from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from src.errors.core import InvalidTokenError


class AuthService:
    """Auth service."""

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_access_token(self, sub: str) -> str:
        token = self.create_access_token({"sub": sub})
        return token

    async def get_token_data(self, token: str) -> dict:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    async def verify_token(
        self, token: str, credentials_exception: Exception = InvalidTokenError()
    ) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user_id = payload.get("user_id")
            if not user_id:
                raise credentials_exception  # noqa
        except JWTError:
            raise credentials_exception

        return user_id

    @staticmethod
    async def get_pin_hash(pin: str) -> str:
        """Hash a PIN using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pin.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    async def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
        """Verify a PIN against its hashed version"""
        return bcrypt.checkpw(plain_pin.encode('utf-8'), hashed_pin.encode('utf-8'))