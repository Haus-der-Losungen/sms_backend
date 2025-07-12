"""User role models"""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.models.base import CoreModel, TimestampMixin, DeleteMixin


class UserRoleBase(CoreModel):
    """Base UserRole Model"""

    role_id: UUID = Field(..., description="ID of role")
    user_id: int = Field(..., description="ID of user")
    assigned_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the role was assigned")


class UserRoleCreate(UserRoleBase):
    pass


class UserRolePublic(UserRoleBase, TimestampMixin):
    pass


class UserRoleInDb(UserRolePublic,DeleteMixin):
    pass