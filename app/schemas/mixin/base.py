from datetime import datetime

from pydantic import BaseModel, field_validator

from app.utils.datetime import UTC


class BaseResponseModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def attach_utc(cls, v: object) -> datetime:
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v
