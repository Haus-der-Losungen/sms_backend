"""Role models"""

from typing import Optional

from pydantic import Field, field_validator

from src.models.base import CoreModel, TimestampMixin, DeleteMixin


class RoleBase(CoreModel):
    """Base Role Model"""

    name: str = Field(..., max_length=25, description="Name of the role")
    description: Optional[str] = Field(None, max_length=255, description="Description of the role")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Role name must not be empty.")
        return name


class RoleCreate(RoleBase):
    """Role creation model"""
    pass


class RoleUpdate(CoreModel):
    """Model for updating role information"""

    name: Optional[str] = Field(None, max_length=25, description="Name of the role")
    description: Optional[str] = Field(None, max_length=255, description="Description of the role")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("Role name must not be empty.")
        return value


class RolePublic(TimestampMixin, RoleBase):
    """Model for outputting role information"""
    pass


class RoleInDb(RolePublic, DeleteMixin):
    """Model for storing role information in the database"""
    pass
