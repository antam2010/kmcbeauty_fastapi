from datetime import datetime
from typing import ClassVar

from pydantic import Field

from app.schemas.mixin.base import BaseResponseModel


class TreatmentMenuDetailBase(BaseResponseModel):
    """시술 상세 정보 기본 스키마."""

    menu_id: int = Field(..., description="시술 메뉴 대분류 ID")
    name: str = Field(..., max_length=255, description="시술 항목명")
    duration_min: int = Field(..., description="기본 시술 시간 (분)")
    base_price: int = Field(..., description="기본 시술 가격 (원)")

    model_config: ClassVar[dict] = {"from_attributes": True}


class TreatmentMenuDetailCreate(TreatmentMenuDetailBase):
    """시술 상세 정보 생성 요청 스키마."""


class TreatmentMenuDetailUpdate(BaseResponseModel):
    """시술 상세 정보 수정 요청 스키마."""

    name: str | None = Field(None, max_length=255, description="시술 항목명")
    duration_min: int | None = Field(None, description="기본 시술 시간 (분)")
    base_price: int | None = Field(None, description="기본 시술 가격 (원)")
    deleted_at: datetime | None = Field(None, description="삭제일시")


class TreatmentMenuDetailInDBBase(TreatmentMenuDetailBase):
    """시술 상세 정보 DB 모델 스키마."""

    id: int = Field(..., description="시술 상세 ID")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")
    deleted_at: datetime | None = Field(None, description="삭제일시")


class TreatmentMenuDetailResponse(TreatmentMenuDetailInDBBase):
    """시술 상세 정보 응답 스키마."""
