from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field

from app.enum.treatment_status import TreatmentStatus


class TreatmentFilterParams(BaseModel):
    page: int = Field(
        default=1,
        ge=1,
        description="페이지 번호 (1부터 시작)",
    )
    page_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="페이지 사이즈 (1~100)",
    )
    start_date: date | None = Field(
        default=None,
        description="예약 시작일 (YYYY-MM-DD)",
    )
    end_date: date | None = Field(
        default=None,
        description="예약 종료일 (YYYY-MM-DD)",
    )
    status: TreatmentStatus | None = Field(
        default=None,
        description="예약 상태 (예약, 대기, 완료, 취소)",
    )
    search: str | None = Field(
        default=None,
        description="예약자 이름, 전화번호, 시술 항목으로 검색합니다.",
    )
    sort_by: str | None = Field(default="reserved_at", description="정렬 기준")
    sort_order: str | None = Field(default="desc", description="정렬 순서 (asc, desc)")


class TreatmentItemCreate(BaseModel):
    menu_detail_id: int = Field(
        ...,
        description="시술 항목 ID",
    )
    duration_min: int = Field(
        ...,
        description="시술 소요 시간 (분)",
    )
    base_price: int = Field(
        ...,
        description="시술 기본 가격",
    )


class TreatmentMenuDetailOut(BaseModel):
    id: int = Field(
        ...,
        description="시술 항목 ID",
    )
    name: str = Field(
        ...,
        description="시술 항목 이름",
    )
    duration_min: int = Field(
        ...,
        ge=0,
        description="시술 소요 시간 (분) 디폴트 값",
    )
    base_price: int = Field(
        ...,
        ge=0,
        description="시술 기본 가격 디폴트 값",
    )

    class Config:
        orm_mode = True


class TreatmentItemRead(BaseModel):
    id: int
    menu_detail_id: int | None = Field(
        default=None,
        description="시술 항목 ID",
    )
    base_price: int = Field(
        ...,
        ge=0,
        description="시술 실제 기본 가격",
    )
    duration_min: int = Field(
        ...,
        ge=0,
        description="시술 실제 소요 시간 (분)",
    )
    menu_detail: TreatmentMenuDetailOut

    class Config:
        orm_mode = True


class TreatmentCreateRequest(BaseModel):
    phonebook_id: int
    reserved_at: datetime
    total_price: int
    status: TreatmentStatus
    finished_at: datetime | None = None
    memo: str | None = None
    items: List[TreatmentItemCreate]

    class Config:
        orm_mode = True


class TreatmentCreateResponse(BaseModel):
    id: int
    phonebook_id: int
    reserved_at: datetime
    total_price: int
    status: TreatmentStatus
    finished_at: datetime | None = None
    memo: str | None = None
    items: List[TreatmentItemCreate]

    class Config:
        orm_mode = True

class TreatmentRead(BaseModel):
    id: int
    phonebook_id: int
    reserved_at: datetime
    memo: str | None
    total_price: int
    status: TreatmentStatus
    finished_at: datetime | None = None
    items: List[TreatmentItemRead]

    class Config:
        orm_mode = True
