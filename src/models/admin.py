"""Admin Model."""

from typing import Optional
from uuid import UUID

from pydantic import Field

from src.models.base import CoreModel, TimestampMixin, DeleteMixin


class AdminBase(CoreModel):
    """Base Admin Model"""

    admin_id: str = Field(..., description="ID of the associated admin")
    is_admin: bool = Field(..., description="Whether the user is an admin")
    permissions: dict = Field(..., description="Permissions of the admin")  # TODO: Add permissions



class AdminCreate(AdminBase):
    """Base Admin Create Model"""

    pass


class AdminUpdate(CoreModel):
    """Model for updating admin information"""

    is_admin: Optional[bool] = Field(None, description="Whether the user is an admin")
    permissions: Optional[dict] = Field(None, description="Permissions of the admin")


class AdminPublic(TimestampMixin, AdminBase):
    """Model for outputting admin information"""

    pass


class AdminInDb(AdminPublic, DeleteMixin):
    """Model for storing admin information in the database"""

    pass
