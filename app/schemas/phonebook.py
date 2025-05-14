from datetime import datetime
from typing import Annotated

from pydantic import Field, field_validator

from app.schemas.base import BaseResponseModel
from app.utils.phone import is_valid_korean_phone_number, normalize_korean_phone_number


# 전화번호 유효성 검사 + 포맷 통일 Mixin
class PhoneNumberValidatorMixin:
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not is_valid_korean_phone_number(v):
            raise ValueError("유효하지 않은 전화번호입니다.")
        return normalize_korean_phone_number(v)


# 전화번호부 생성 요청 스키마
class PhonebookCreate(BaseResponseModel, PhoneNumberValidatorMixin):
    group_name: str | None = Field(
        default=None, max_length=100, description="그룹 이름"
    )
    memo: str | None = Field(default=None, description="메모")
    name: str = Field(..., max_length=100, description="이름")
    phone_number: Annotated[str, Field(max_length=20, description="전화번호")]


# 전화번호부 수정 요청 스키마
class PhonebookUpdate(BaseResponseModel, PhoneNumberValidatorMixin):
    group_name: str | None = Field(
        default=None, max_length=100, description="그룹 이름"
    )
    memo: str | None = Field(default=None, description="메모")
    name: str | None = Field(default=None, max_length=100, description="이름")
    phone_number: str | None = Field(
        default=None, max_length=20, description="전화번호"
    )


# 전화번호부 목록 요청 (필터링용)
class PhonebookFilter(BaseResponseModel):
    search: str | None = Field(
        default=None, description="검색어 (이름, 전화번호, 그룹명, 메모 등)"
    )


# 전화번호부 그룹 별 응답
class PhonebookGroupedByGroupnameResponse(BaseResponseModel):
    group_name: str = Field(..., description="그룹 이름")
    count: int = Field(..., description="전화번호부 개수")
    items: list["PhonebookResponse"] = Field(
        default=[], description="전화번호부 목록"
    )
    model_config = {"from_attributes": True}
    


# 전화번호부 응답 스키마
class PhonebookResponse(BaseResponseModel):
    id: int = Field(..., description="전화번호부 ID")
    shop_id: int = Field(..., description="상점 ID")
    group_name: str | None = Field(None, max_length=100, description="그룹 이름")
    name: str = Field(..., max_length=100, description="이름")
    phone_number: str = Field(..., max_length=20, description="전화번호")
    memo: str | None = Field(None, description="메모")
    created_at: datetime = Field(..., description="생성일")
    updated_at: datetime = Field(..., description="수정일")

    model_config = {"from_attributes": True}
