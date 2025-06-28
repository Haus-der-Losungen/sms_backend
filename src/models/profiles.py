"""Profile models."""

from typing import Optional
from uuid import UUID

from pydantic import Field, validator

from src.models.base import (CoreModel,TimestampMixin,UUIDMixin,DeleteMixin,UserIDModelMixin,)


class ProfileBase(CoreModel):
    """Base Profile Model"""

    user_id: Optional[UUID] = Field(None, description="ID of the associated user")
    first_name: str = Field(..., max_length=50, description="First name of the user")
    last_name: str = Field(..., max_length=50, description="Last name of the user")
    phone: str = Field(..., max_length=20, description="Phone number of the user")
    gender: str = Field(..., max_length=10, description="Gender of user")
    user_role: str = Field(..., max_length=20, description="role of user")

    @validator("phone")
    def validate_phone(cls, value: str) -> str:
        """Validates that the phone number contains only digits and is of appropriate length."""
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")
        if not (7 <= len(value) <= 20):
            raise ValueError("Phone number must be between 7 and 20 digits.")
        return value

    @validator("gender")
    def validate_gender(cls, gender: str) -> str:
        """Validates that the gender is one of the accepted values."""
        allowed_genders = {"male", "female"}
        if gender.lower() not in allowed_genders:
            raise ValueError(f"Gender must be one of {allowed_genders}.")
        return gender.capitalize()


class ProfileCreate(ProfileBase):
    """Profile creation model"""

    email: Optional[str] = Field(None, description="Email address of the user")


class ProfileUpdate(CoreModel):
    """Model for updating profile information"""

    first_name: Optional[str] = Field(None, max_length=50, description="First name of the user")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name of the user")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number of the user")
    gender: Optional[str] = Field(None, max_length=10, description="Gender of the user")
    user_type: Optional[str] = Field(None, max_length=20, description="Type of user")
   

    @validator("phone")
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """Validates that the phone number contains only digits and is of appropriate length."""
        if value is not None:
            if not value.isdigit():
                raise ValueError("Phone number must contain only digits.")
            if not (7 <= len(value) <= 20):
                raise ValueError("Phone number must be between 7 and 20 digits.")
        return value

    @validator("gender")
    def validate_gender(cls, value: Optional[str]) -> Optional[str]:
        """Validates that the gender is one of the accepted values."""
        if value is not None:
            allowed_genders = {"male", "female", "other"}
            if value.lower() not in allowed_genders:
                raise ValueError(f"Gender must be one of {allowed_genders}.")
            return value.capitalize()
        return value


class ProfilePublic(TimestampMixin, UUIDMixin, ProfileBase, UserIDModelMixin):
    """Model for outputting profile information"""

    email: str = Field(..., description="Email address of the user")


class ProfileInDb(ProfilePublic, DeleteMixin):
    """Model for storing profile information in the database"""

    pass