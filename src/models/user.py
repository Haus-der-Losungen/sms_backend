"""
User Model
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, Field

from src.models.base import CoreModel, TimestampMixin, DeleteMixin, UserIDModelMixin

class UserBase(CoreModel):
    email: EmailStr = Field(..., description="user email")
    role: str = Field(..., description="user role")

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: str):
        return value.lower()

class UserCreate(UserBase):
    password_hash: str = Field(..., description="hashed user password")

class UserUpdate(CoreModel):
     email: EmailStr = Field(..., description="updated user email")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")

class UserPublic(TimestampMixin, DeleteMixin, UserBase, UserIDModelMixin):
    role: Optional[str] = Field(None)

class UserInDb(UserPublic):
    password_hash : str = Field(..., description ="Hashed user password" )
