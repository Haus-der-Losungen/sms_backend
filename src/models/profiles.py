"""Profile models."""

from typing import Optional
from uuid import UUID
from pydantic import Field, EmailStr, field_validator

from src.models.base import (
    CoreModel,
    TimestampMixin,
    DeleteMixin,
    UserIDModelMixin,
)
from src.enums.gender import GenderEnum
from src.enums.marital_status import MaritalStatusEnum



# Base model for profile creation - minimal fields only
class ProfileBase(CoreModel):
    """Base profile model with core fields"""
    first_name: str = Field(..., max_length=50, description="First name of the user")
    last_name: str = Field(..., max_length=50, description="Last name of the user")
    phone: str = Field(..., max_length=20, description="Phone number of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    gender: GenderEnum = Field(..., description="Gender of user")
    date_of_birth: str = Field(..., description="Date of birth in YYYY-MM-DD format")
    photo: str = Field(..., description="Photo path or URL")
    marital_status: MaritalStatusEnum = Field(..., description="Marital status")
    emergency_contact: str = Field(..., description="Emergency contact")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")
        if not (7 <= len(value) <= 20):
            raise ValueError("Phone number must be between 7 and 20 digits.")
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, gender: GenderEnum) -> GenderEnum:
        return gender

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: EmailStr) -> EmailStr:
        return value.lower()

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: str) -> str:
        if not value:
            raise ValueError("Date of birth is required.")
        return value
    
    @field_validator("photo")
    @classmethod
    def validate_photo(cls, value: str) -> str:
        if not value:
            raise ValueError("Photo is required.")
        return value
    
    @field_validator("emergency_contact")
    @classmethod
    def validate_emergency_contact(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")
        if not (7 <= len(value) <= 20):
            raise ValueError("Phone number must be between 7 and 20 digits.")
        return value


# Model for profile creation - no IDs
class ProfileCreate(ProfileBase):
    """Model for creating a new profile"""
    pass


# Model for updating profile - all fields optional
class ProfileUpdate(CoreModel):
    """Model for updating profile information"""

    first_name: Optional[str] = Field(None, max_length=50, description="First name of the user")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name of the user")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number of the user")
    email: Optional[EmailStr] = Field(None, description="Email address of the user")
    gender: Optional[GenderEnum] = Field(None, description="Gender of user")
    date_of_birth: Optional[str] = Field(None, description="Date of birth in YYYY-MM-DD format")
    photo: Optional[str] = Field(None, description="Photo path or URL")
    marital_status: Optional[MaritalStatusEnum] = Field(None, description="Marital status")
    emergency_contact: Optional[str] = Field(None, description="Emergency contact")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if not value.isdigit():
                raise ValueError("Phone number must contain only digits.")
            if not (7 <= len(value) <= 20):
                raise ValueError("Phone number must be between 7 and 20 digits.")
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: Optional[GenderEnum]) -> Optional[GenderEnum]:
        return value

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, value: Optional[EmailStr]) -> Optional[EmailStr]:
        return value.lower() if value else value
    
    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: str) -> str:
        if not value:
            raise ValueError("Date of birth is required.")
        return value
    
    @field_validator("photo")
    @classmethod
    def validate_photo(cls, value: str) -> str:
        if not value:
            raise ValueError("Photo is required.")
        return value
    
    @field_validator("emergency_contact")
    @classmethod
    def validate_emergency_contact(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")
        if not (7 <= len(value) <= 20):
            raise ValueError("Phone number must be between 7 and 20 digits.")
        return value



# Model for public API responses - includes IDs and timestamps
class ProfilePublic(TimestampMixin, ProfileBase):
    """Model for public profile information in API responses"""
    profile_id: Optional[str] = None
    user_id: Optional[str] = None


# Model for database objects - includes soft delete
class ProfileInDb(ProfilePublic, DeleteMixin):
    """Model for profile data as stored in database"""
    pass
