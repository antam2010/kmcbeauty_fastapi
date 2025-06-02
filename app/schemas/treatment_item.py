from datetime import datetime
from typing import ClassVar

from pydantic import Field

from app.schemas.mixin.base import BaseResponseModel
from app.schemas.treatment_menu_detail import TreatmentMenuDetailBase


class TreatmentItemBase(BaseResponseModel):
    """시술 항목 기본 스키마."""

    treatment_id: int = Field(..., description="시술 예약 ID")
    menu_detail_id: int | None = Field(None, description="시술 상세 ID")
    base_price: int = Field(0, description="기본 가격")
    duration_min: int = Field(0, description="소요 시간 (분)")
    session_no: int = Field(1, description="시술 회차")

    menu_detail: TreatmentMenuDetailBase = Field(
        None,
        description="시술 항목 상세 정보",
    )

    model_config: ClassVar[dict] = {"from_attributes": True}


class TreatmentItemSimple(BaseResponseModel):
    """시술 항목 간단 정보 스키마."""

    session_no: int = Field(1, description="시술 회차")
    menu_detail: TreatmentMenuDetailBase = Field(
        None,
        description="시술 항목 상세 정보",
    )

    model_config: ClassVar[dict] = {"from_attributes": True}


class TreatmentItemCreate(BaseResponseModel):
    """시술 항목 생성 요청 스키마."""

    menu_detail_id: int = Field(..., description="시술 상세 ID")
    base_price: int = Field(..., description="기본 가격")
    duration_min: int = Field(..., description="소요 시간 (분)")
    session_no: int = Field(..., description="시술 회차", ge=1)


class TreatmentItemUpdate(BaseResponseModel):
    """시술 항목 수정 요청 스키마."""

    id: int | None = Field(None, description="시술 항목 ID")
    menu_detail_id: int | None = Field(None, description="시술 상세 ID")
    base_price: int | None = Field(None, description="기본 가격")
    duration_min: int | None = Field(None, description="소요 시간 (분)")
    session_no: int | None = Field(None, description="시술 회차", ge=1)


class TreatmentItemInDBBase(TreatmentItemBase):
    """시술 항목 DB 모델 스키마."""

    id: int = Field(..., description="시술 항목 ID")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")

    model_config: ClassVar[dict] = {"from_attributes": True}


class TreatmentItemResponse(TreatmentItemInDBBase):
    """시술 항목 응답 스키마."""
