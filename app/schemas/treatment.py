from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.enum.treatment_status import TreatmentStatus


class TreatmentItemCreate(BaseModel):
    menu_detail_id: int


class TreatmentItemRead(BaseModel):
    id: int
    menu_detail_id: int | None

    class Config:
        orm_mode = True


class TreatmentCreate(BaseModel):
    phonebook_id: int
    reserved_at: datetime
    total_price: int
    status: TreatmentStatus
    finished_at: datetime | None = None
    memo: str | None = None
    items: List[TreatmentItemCreate]


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
