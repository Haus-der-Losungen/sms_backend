"""
User Model
"""
from ast import pattern
from typing import Optional
from pydantic import  BaseModel, constr, field_validator, Field

from src.models.base import CoreModel, TimestampMixin, DeleteMixin, UserIDModelMixin

class UserBase(CoreModel):
    role: str = Field(..., description="user role")

class UserCreate(UserBase):
    pin_hash: str = Field(min_length=6,max_length=6, pattern=r"^\d+$", description="user pin")

class UserUpdate(CoreModel):
    pin_hash: str = Field(min_length=6,max_length=6, pattern= r"^\d+$", description="user pin")

class UserLogin(BaseModel):
    pin_hash: str = Field(min_length=6,max_length=6, pattern= r"^\d+$", description="user pin")

class UserPublic(TimestampMixin, DeleteMixin, UserBase, UserIDModelMixin):
    role: Optional[str] = Field(None)

class UserInDb(UserPublic):
    pin_hash: str = Field( min_length=6,max_length=6, pattern=r"^\d+$", description="user pin")
