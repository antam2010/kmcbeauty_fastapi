from pydantic import BaseModel, field_validator
from datetime import datetime, timezone

class BaseResponseModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def attach_utc(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
