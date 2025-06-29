"""User type enum."""

from enum import Enum

class UserRole(str, Enum):
    """Enum for user roles."""

    STUDENT = "student"
    Staff = "staff"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"