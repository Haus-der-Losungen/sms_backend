"""User Profile Model"""

from typing import Optional

from src.models.base import CoreModel
from src.models.profiles import ProfileCreate, ProfileInDb, ProfilePublic
from src.models.user import UserCreate, UserInDb, UserPublic


class UserProfileCreate(CoreModel):
    """User Profile create model"""

    user: UserCreate
    profile: ProfileCreate


class UserProfileInDb(CoreModel):
    """User Profile in db model"""

    user: UserInDb
    profile: ProfileInDb


class UserProfilePublic(CoreModel):
    """User Profile public model"""

    user: UserPublic
    profile: ProfilePublic
