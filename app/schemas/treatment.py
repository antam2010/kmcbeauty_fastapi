from datetime import date, datetime
from typing import Annotated

from pydantic import Field

from app.enum.treatment_status import TreatmentStatus
from app.schemas.base import BaseResponseModel
from app.schemas.phonebook import PhonebookResponse


# =========================
# 필터 요청 스키마
# =========================
class TreatmentFilter(BaseResponseModel):
    start_date: date | None = Field(None, description="예약 시작일 (YYYY-MM-DD)")
    end_date: date | None = Field(None, description="예약 종료일 (YYYY-MM-DD)")
    status: TreatmentStatus | None = Field(
        None, description="예약 상태 (예약, 대기, 완료, 취소)"
    )
    search: str | None = Field(
        None, description="예약자 이름, 전화번호, 시술 항목 검색어"
    )
    sort_by: str = Field(default="reserved_at", description="정렬 기준 필드명")
    sort_order: str = Field(default="desc", description="정렬 순서 (asc, desc)")


# =========================
# 시술 항목 관련 스키마
# =========================
class TreatmentItemCreate(BaseResponseModel):
    menu_detail_id: int = Field(..., description="시술 항목 ID")
    duration_min: Annotated[int, Field(ge=0, description="시술 소요 시간 (분)")]
    base_price: Annotated[int, Field(ge=0, description="시술 기본 가격")]


class TreatmentItemResponse(BaseResponseModel):
    id: int = Field(..., description="시술 항목 ID")
    base_price: Annotated[int, Field(ge=0, description="실제 적용 기본 가격")]
    duration_min: Annotated[int, Field(ge=0, description="실제 적용 소요 시간 (분)")]

    model_config = {"from_attributes": True}


# =========================
# 📝 예약 등록 요청 및 응답
# =========================
class TreatmentCreate(BaseResponseModel):
    phonebook_id: int = Field(..., description="예약자 전화번호부 ID")
    reserved_at: datetime = Field(..., description="예약 일시")
    status: TreatmentStatus = Field(..., description="예약 상태")
    finished_at: datetime | None = Field(None, description="시술 완료 일시")
    memo: str | None = Field(None, description="예약 메모")
    treatment_items: list[TreatmentItemCreate] = Field(
        ..., description="시술 항목 리스트"
    )

    model_config = {"from_attributes": True}


class TreatmentResponse(BaseResponseModel):
    id: int = Field(..., description="예약 ID")
    phonebook_id: int = Field(..., description="예약자 전화번호부 ID")
    reserved_at: datetime = Field(..., description="예약 일시")
    status: TreatmentStatus = Field(..., description="예약 상태")
    finished_at: datetime | None = Field(None, description="시술 완료 일시")
    memo: str | None = Field(None, description="예약 메모")
    treatment_items: list[TreatmentItemResponse] = Field(
        ..., description="시술 항목 리스트"
    )

    model_config = {"from_attributes": True}


# =========================
# 📄 단일 조회 / 목록 응답
# =========================
class TreatmentDetail(BaseResponseModel):
    id: int = Field(..., description="예약 ID")
    phonebook_id: int = Field(..., description="예약자 전화번호부 ID")
    reserved_at: datetime = Field(..., description="예약 일시")
    memo: str | None = Field(None, description="예약 메모")
    status: TreatmentStatus = Field(..., description="예약 상태")
    finished_at: datetime | None = Field(None, description="시술 완료 일시")
    treatment_items: list[TreatmentItemResponse] = Field(
        ..., description="시술 항목 리스트"
    )
    phonebook: PhonebookResponse = Field(..., description="예약자 정보")

    model_config = {"from_attributes": True}
