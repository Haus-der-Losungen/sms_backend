"""User Profile Model"""

from typing import Optional

from src.models.base import CoreModel
from src.models.profiles import ProfileCreate, ProfileInDb, ProfilePublic
from src.models.user import UserCreate, UserInDb, UserPublic


# Model for user profile creation - combines user and profile creation
class UserProfileCreate(CoreModel):
    """Model for creating a new user with profile"""
    user: UserCreate
    profile: ProfileCreate


# Model for database objects - includes full user and profile data
class UserProfileInDb(CoreModel):
    """Model for user profile data as stored in database"""
    user: UserInDb
    profile: ProfileInDb


# Model for public API responses - includes public user and profile data
class UserProfilePublic(CoreModel):
    """Model for public user profile information in API responses"""
    user: UserPublic
    profile: ProfilePublic


# Model for user creation response - shows IDs and PIN
class UserProfileCreateResponse(CoreModel):
    """Response model for user creation, includes user_id, pin, and profile_id"""
    user_id: str
    pin: str
    profile_id: str
