from pydantic import BaseModel, Field
from datetime import datetime

class PhonebookCreate(BaseModel):
    group_name: str | None = Field(None, max_length=100)
    name: str = Field(..., max_length=100, description="이름")
    phone_number: str = Field(..., max_length=20, description="전화번호")
    memo: str | None = Field(None, description="메모")


class PhonebookUpdate(BaseModel):
    group_name: str | None = Field(None, max_length=100)
    name: str | None = Field(None, max_length=100)
    phone_number: str | None = Field(None, max_length=20)
    memo: str | None = Field(None)


class PhonebookResponse(BaseModel):
    id: int
    user_id: int
    group_name: str | None
    name: str
    phone_number: str
    memo: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True