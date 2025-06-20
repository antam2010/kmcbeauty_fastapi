from datetime import date, datetime
from typing import ClassVar

from pydantic import Field, model_validator

from app.enum.treatment_status import PaymentMethod, TreatmentStatus
from app.schemas.mixin.base import BaseModel, BaseResponseModel
from app.schemas.phonebook import PhonebookResponse
from app.schemas.treatment_item import (
    TreatmentItemCreate,
    TreatmentItemResponse,
    TreatmentItemUpdate,
)
from app.schemas.user import UserBase


class TreatmentBase(BaseResponseModel):
    """시술 정보의 기본 스키마."""

    phonebook_id: int = Field(..., description="시술 대상 고객 ID")
    reserved_at: datetime = Field(..., description="예약 일시")
    memo: str | None = Field(None, description="메모")
    status: TreatmentStatus = Field(..., description="예약 상태")
    finished_at: datetime | None = Field(None, description="시술 완료일시")
    payment_method: PaymentMethod = Field(
        PaymentMethod.CARD,
        description="결제 수단",
    )
    staff_user_id: int | None = Field(
        None,
        description="시술 담당자 유저 ID",
        ge=1,
    )


class TreatmentCreate(TreatmentBase):
    """시술 생성 스키마."""

    treatment_items: list[TreatmentItemCreate] = Field(
        default_factory=list,
        description="시술 항목 리스트",
    )


class TreatmentUpdate(TreatmentBase):
    """시술 수정 스키마."""

    treatment_items: list[TreatmentItemUpdate] = Field(
        default_factory=list,
        description="시술 항목 리스트",
    )


class TreatmentInDBBase(TreatmentBase):
    """DB에 저장된 시술 기본 스키마."""

    id: int = Field(..., description="시술 예약 ID")
    shop_id: int = Field(..., description="상점 ID")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")
    created_user_id: int | None = Field(
        ...,
        description="예약 생성자 유저 ID",
    )

    model_config: ClassVar[dict] = {"from_attributes": True}


class TreatmentResponse(TreatmentInDBBase):
    """시술 조회 스키마."""

    status_label: str = Field(
        None,
        description="예약 상태 라벨",
    )
    payment_method_label: str = Field(
        None,
        description="결제 수단 라벨",
    )

    @model_validator(mode="after")
    def fill_label(self) -> str:
        self.status_label = self.status.label
        return self

    @model_validator(mode="after")
    def fill_payment_method_label(self) -> str:
        self.payment_method_label = self.payment_method.label
        return self

    treatment_items: list[TreatmentItemResponse] = Field(
        ...,
        description="시술 항목 리스트",
    )
    phonebook: PhonebookResponse = Field(
        ...,
        description="시술 대상 고객 정보",
    )

    staff_user: UserBase | None = Field(
        None,
        description="시술 담당자 유저 정보",
    )


class TreatmentFilter(BaseModel):
    """시술 필터링 스키마."""

    start_date: date | None = Field(None, description="예약 시작일 (YYYY-MM-DD)")
    end_date: date | None = Field(None, description="예약 종료일 (YYYY-MM-DD)")
    status: TreatmentStatus | None = Field(
        None,
        description="예약 상태 (예약, 대기, 완료, 취소)",
    )
    search: str | None = Field(
        None,
        description="예약자 이름, 전화번호, 시술 항목 검색어",
    )
    sort_by: str = Field(default="reserved_at", description="정렬 기준 필드명")
    sort_order: str = Field(default="desc", description="정렬 순서 (asc, desc)")
    staff_user_id: int | None = Field(
        None,
        description="시술 담당자 유저 ID",
    )


class TreatmentAutoComplete(BaseResponseModel):
    """시술 자동 완료 스키마."""

    treatment_id: int = Field(..., description="시술 예약 ID")
    reserved_at: datetime = Field(..., description="예약 일시")
    total_duration_min: int = Field(..., description="총 시술 시간 (분)")
    status: TreatmentStatus = Field(..., description="시술 상태")
    finished_at: datetime | None = Field(None, description="시술 완료일시")


class TreatmentSimpleResponse(BaseResponseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[dict] = {"from_attributes": True}
