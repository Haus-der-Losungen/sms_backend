from pydantic import BaseModel, Field, constr
from typing import Optional

from src.enums.users import UserRole
from src.models.base import CoreModel, TimestampMixin, DeleteMixin, UserIDModelMixin

# Base model for user creation - minimal fields only
class UserBase(CoreModel):
    """Base user model with common fields"""
    role: UserRole = Field(UserRole.STUDENT, description="User Role")

# Model for user creation - no IDs, PIN is optional (will be auto-generated if not provided)
class UserCreate(UserBase):
    """Model for creating a new user"""
    pin: Optional[str] = Field(None, description="User PIN (plain text, optional - will be auto-generated if not provided)")

# Model for updating user - only role can be updated
class UserUpdate(CoreModel):
    """Model for updating user information"""
    role: UserRole = Field(UserRole.STUDENT, description="User Role")

# Model for user login
class UserLogin(BaseModel):
    """Model for user login"""
    pin: str = Field(..., min_length=4, max_length=10, description="User PIN (plain text)")
    user_id: str = Field(..., description="User ID")

# Model for public API responses - includes IDs and timestamps
class UserPublic(TimestampMixin, DeleteMixin, UserBase, UserIDModelMixin):
    """Model for public user information in API responses"""
    role: UserRole = Field(UserRole.STUDENT, description="User Role")

# Model for database objects - includes hashed PIN
class UserInDb(UserPublic):
    """Model for user data as stored in database"""
    pin_hash: constr(min_length=6, max_length=268) = Field(..., description="User PIN (hashed)")  # type: ignore

# Model for /me endpoint - shows user ID and hashed PIN
class UserMe(CoreModel):
    """Model for /me endpoint - shows user ID and PIN hash"""
    user_id: str = Field(..., description="User ID")
    pin_hash: constr(min_length=6, max_length=268) = Field(..., description="User PIN (hashed)")  # type: ignore
