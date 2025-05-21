from datetime import UTC, datetime

from pydantic import BaseModel, field_validator


class BaseResponseModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def attach_utc(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v
