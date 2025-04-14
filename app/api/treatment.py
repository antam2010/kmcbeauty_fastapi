from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.treatment import TreatmentCreate, TreatmentFilterParams, TreatmentRead
from app.services.treatment_service import (
    create_treatment_service,
    get_treatment_list_service,
)

router = APIRouter(prefix="/treatments", tags=["시술 예약"])


# 시술 예약 생성
@router.post("/", response_model=TreatmentRead, summary="시술 예약 생성", description="시술 예약을 생성합니다.")
def create_treatment_api(
    data: TreatmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_treatment_service(data, db, current_user)


# 시술 예약 목록 조회
@router.get(
    "/",
    response_model=list[TreatmentRead],
    summary="시술 예약 목록 조회",
    description="시술 예약 목록을 조회합니다.",
)
def list_treatments_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    filters: TreatmentFilterParams = Depends(),
):
    return get_treatment_list_service(
        db=db,
        current_user=current_user,
        filters=filters,
    )
