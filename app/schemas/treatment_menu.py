from typing import Optional

from pydantic import BaseModel


class TreatmentMenuCreate(BaseModel):
    name: str


class TreatmentMenuDetailCreate(BaseModel):
    name: str
    duration_min: int
    base_price: int
