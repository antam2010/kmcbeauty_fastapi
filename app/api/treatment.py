from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

from app.core.auth import get_current_user
from app.models.user import User

from app.schemas.treatment import TreatmentCreate, TreatmentRead
from app.services.treatment_service import create_treatment


router = APIRouter(prefix="/treatments", tags=["시술 예약"])

@router.post("/", response_model=TreatmentRead)
def create_treatment_api(data: TreatmentCreate, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    return create_treatment(data, db, current_user)
