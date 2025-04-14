from datetime import datetime

from pydantic import BaseModel, Field


# 전화번호부 리스트 조회 요청 스키마
class PhonebookListRequest(BaseModel):
    group_name: str | None = Field(None, description="그룹 이름", max_length=100)


# 전화번호부 생성 요청 스키마
class PhonebookCreate(BaseModel):
    group_name: str | None = Field(None, max_length=100, description="그룹 이름")
    name: str = Field(..., max_length=100, description="이름")
    phone_number: str = Field(..., max_length=20, description="전화번호")
    memo: str | None = Field(None, description="메모")


# 전화번호부 수정 요청 스키마 (모든 필드 선택적)
class PhonebookUpdate(BaseModel):
    group_name: str | None = Field(None, max_length=100, description="그룹 이름")
    name: str | None = Field(None, max_length=100, description="이름")
    phone_number: str | None = Field(None, max_length=20, description="전화번호")
    memo: str | None = Field(None, description="메모")


# 전화번호부 단일 항목 응답 스키마
class PhonebookResponse(BaseModel):
    id: int = Field(..., description="전화번호부 ID")
    user_id: int = Field(..., description="사용자 ID")
    group_name: str | None = Field(None, max_length=100, description="그룹 이름")
    name: str = Field(..., max_length=100, description="이름")
    phone_number: str = Field(..., max_length=20, description="전화번호")
    memo: str | None = Field(None, description="메모")
    created_at: datetime = Field(..., description="생성일")
    updated_at: datetime = Field(..., description="수정일")

    class Config:
        from_attributes = True
