from pydantic import BaseModel
from typing import Optional


class TreatmentMenuCreate(BaseModel):
    name: str


class TreatmentMenuDetailCreate(BaseModel):
    name: str
    duration_min: int
    base_price: int
