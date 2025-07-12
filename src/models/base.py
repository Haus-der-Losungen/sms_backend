from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, model_validator


# Factory for current UTC timestamp
def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


# Base model with common configuration
class CoreModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
    )

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, data: Any) -> Any:
        # Placeholder for any pre-processing if needed
        return data


# Timestamp Mixin for created/updated fields
class TimestampMixin(CoreModel):
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime = Field(default_factory=datetime_now)


# Soft delete Mixin
class DeleteMixin(CoreModel):
    is_deleted: bool = False


# Mixin to associate with a user
class UserIDModelMixin(CoreModel):
    user_id: str  # or UUID
