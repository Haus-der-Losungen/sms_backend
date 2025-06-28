from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class CoreModel(BaseModel):
    class Config:
        from_attributes = True
        validate_assignment = True
        extra = "forbid"
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    @model_validator(mode="before")
    @classmethod
    def convert_all_uuids(cls, data: Any) -> Any:
        """Convert all UUID values to strings recursively."""
        if isinstance(data, dict):
            return {
                key: (
                    str(value)
                    if isinstance(value, UUID)
                    else cls.convert_all_uuids(value)
                )
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [cls.convert_all_uuids(item) for item in data]
        return data

    def model_dump(self, **kwargs):
        """Override model_dump to ensure UUIDs are converted to strings."""
        data = super().model_dump(**kwargs)
        return self.convert_all_uuids(data)



class IDMixin(BaseModel):
    id: int


class UUIDMixin(BaseModel):
    id: UUID


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin(BaseModel):
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime = Field(default_factory=datetime_now)


class DeleteMixin(BaseModel):
    is_deleted: bool = False

class UserIDModelMixin(BaseModel):
    """User ID data."""

    user_id: UUID
