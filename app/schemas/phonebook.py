from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.utils.phone import is_valid_korean_phone_number, normalize_korean_phone_number


# 공통 필드 유효성 검사용 Mixin
class PhoneNumberValidatorMixin:
    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not is_valid_korean_phone_number(v):
            raise ValueError("유효하지 않은 전화번호입니다.")
        return normalize_korean_phone_number(v)


# CREATE 요청 전용 스키마
class PhonebookCreate(BaseModel, PhoneNumberValidatorMixin):
    group_name: str | None = Field(
        default=None, max_length=100, description="그룹 이름"
    )
    memo: str | None = Field(default=None, description="메모")
    name: str = Field(..., max_length=100, description="이름")
    phone_number: str = Field(..., max_length=20, description="전화번호")


# UPDATE 요청 전용 스키마 (모든 필드 선택적)
class PhonebookUpdate(BaseModel, PhoneNumberValidatorMixin):
    group_name: str | None = Field(
        default=None, max_length=100, description="그룹 이름"
    )
    memo: str | None = Field(default=None, description="메모")
    name: str | None = Field(default=None, max_length=100, description="이름")
    phone_number: str | None = Field(
        default=None, max_length=20, description="전화번호"
    )


# LIST 필터링 요청용
class PhonebookRequest(BaseModel):
    group_name: str | None = Field(
        default=None, description="그룹 이름", max_length=100
    )


# 응답용 스키마
class PhonebookResponse(BaseModel):
    id: int = Field(..., description="전화번호부 ID")
    shop_id: int = Field(..., description="상점 ID")
    group_name: str | None = Field(None, max_length=100, description="그룹 이름")
    name: str = Field(..., max_length=100, description="이름")
    phone_number: str = Field(..., max_length=20, description="전화번호")
    memo: str | None = Field(None, description="메모")
    created_at: datetime = Field(..., description="생성일")
    updated_at: datetime = Field(..., description="수정일")
