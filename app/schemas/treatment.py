from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.enum.treatment_status import TreatmentStatus


# 시술 예약 목록 필터 요청 파라미터
class TreatmentFilterParams(BaseModel):
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


# 시술 항목 생성 요청
class TreatmentItemCreate(BaseModel):
    menu_detail_id: int = Field(..., description="시술 항목 ID")
    duration_min: Annotated[int, Field(ge=0, description="시술 소요 시간 (분)")]
    base_price: Annotated[int, Field(ge=0, description="시술 기본 가격")]


# 시술 항목 내부 메뉴 상세 정보
class TreatmentMenuDetailOut(BaseModel):
    id: int = Field(..., description="메뉴 상세 ID")
    name: str = Field(..., description="메뉴 상세 이름")
    duration_min: Annotated[int, Field(ge=0, description="기본 소요 시간 (분)")]
    base_price: Annotated[int, Field(ge=0, description="기본 가격")]

    model_config = {"from_attributes": True}


# 시술 항목 조회 응답
class TreatmentItemRead(BaseModel):
    id: int = Field(..., description="시술 항목 ID")
    menu_detail_id: int | None = Field(None, description="연결된 메뉴 상세 ID")
    base_price: Annotated[int, Field(ge=0, description="실제 적용 기본 가격")]
    duration_min: Annotated[int, Field(ge=0, description="실제 적용 소요 시간 (분)")]
    menu_detail: TreatmentMenuDetailOut = Field(
        ..., description="연결된 메뉴 상세 정보"
    )

    model_config = {"from_attributes": True}


# 시술 예약 생성 요청
class TreatmentCreateRequest(BaseModel):
    phonebook_id: int = Field(..., description="예약자 전화번호부 ID")
    reserved_at: datetime = Field(..., description="예약 일시")
    total_price: int = Field(..., description="총 예약 가격")
    status: TreatmentStatus = Field(..., description="예약 상태")
    finished_at: datetime | None = Field(None, description="시술 완료 일시")
    memo: str | None = Field(None, description="예약 메모")
    items: list[TreatmentItemCreate] = Field(..., description="시술 항목 리스트")

    model_config = {"from_attributes": True}


# 시술 예약 생성 응답
class TreatmentCreateResponse(BaseModel):
    id: int = Field(..., description="예약 ID")
    phonebook_id: int = Field(..., description="예약자 전화번호부 ID")
    reserved_at: datetime = Field(..., description="예약 일시")
    total_price: int = Field(..., description="총 예약 가격")
    status: TreatmentStatus = Field(..., description="예약 상태")
    finished_at: datetime | None = Field(None, description="시술 완료 일시")
    memo: str | None = Field(None, description="예약 메모")
    items: list[TreatmentItemCreate] = Field(..., description="시술 항목 리스트")

    model_config = {"from_attributes": True}


# 시술 예약 단일 조회 및 목록 응답
class TreatmentRead(BaseModel):
    id: int = Field(..., description="예약 ID")
    phonebook_id: int = Field(..., description="예약자 전화번호부 ID")
    reserved_at: datetime = Field(..., description="예약 일시")
    memo: str | None = Field(None, description="예약 메모")
    total_price: int = Field(..., description="총 예약 가격")
    status: TreatmentStatus = Field(..., description="예약 상태")
    finished_at: datetime | None = Field(None, description="시술 완료 일시")
    items: list[TreatmentItemRead] = Field(..., description="시술 항목 리스트")

    model_config = {"from_attributes": True}
