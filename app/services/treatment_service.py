from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.treatment import create_treatment_with_items, get_treatment_list

from app.models.treatment import Treatment
from app.models.user import User

from app.schemas.treatment import TreatmentCreateRequest, TreatmentFilterParams, TreatmentCreateResponse

import logging


# 시술 예약을 생성 서비스
def create_treatment_service(data: TreatmentCreateRequest, db: Session, current_user: User) -> TreatmentCreateResponse:
    try:
        return create_treatment_with_items(db, data, current_user)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error creating treatment: {e}")
        raise HTTPException(status_code=500)


# 시술 예약 목록 조회 서비스
def get_treatment_list_service(
    db: Session, current_user: User, filters: TreatmentFilterParams
) -> list[Treatment]:
    try:
        return get_treatment_list(db=db, user=current_user, filters=filters)
    except Exception:
        raise HTTPException(status_code=500)
