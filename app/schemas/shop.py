from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.utils.phone import is_valid_korean_phone_number, normalize_korean_phone_number


class ShopBase(BaseModel):
    name: str = Field(..., description="샵 이름", min_length=2, max_length=255)
    address: str = Field(..., description="주소", min_length=2, max_length=255)
    address_detail: str | None = Field(None, description="상세 주소", max_length=255)
    phone: str | None = Field(None, description="전화번호", max_length=20)
    business_number: str | None = Field(
        None, description="사업자 등록번호", max_length=20
    )


class ShopPhoneValidatorMixin:
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v and not is_valid_korean_phone_number(v):
            raise ValueError("유효하지 않은 전화번호입니다.")
        return normalize_korean_phone_number(v)


class ShopCreate(ShopBase, ShopPhoneValidatorMixin):
    class Config:
        orm_mode = True


class ShopUpdate(ShopBase, ShopPhoneValidatorMixin):
    class Config:
        orm_mode = True


class ShopResponse(ShopBase):
    id: int = Field(..., description="샵 ID")
    created_at: datetime = Field(..., description="생성일")
    updated_at: datetime = Field(..., description="수정일")

    class Config:
        orm_mode = True
