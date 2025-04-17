import logging

from fastapi import status
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.crud.treatment import create_treatment_with_items, get_treatment_list
from app.exceptions import CustomException
from app.models.shop import Shop
from app.models.treatment import Treatment
from app.models.user import User
from app.schemas.treatment import (
    TreatmentCreateRequest,
    TreatmentCreateResponse,
    TreatmentFilterParams,
)

DOMAIN = "TREATMENT"


# 시술 예약 생성 서비스
def create_treatment_service(
    data: TreatmentCreateRequest, db: Session, current_shop: Shop
) -> TreatmentCreateResponse:
    try:
        return create_treatment_with_items(db, data, current_shop.id)
    except ValueError:
        logging.exception(f"Invalid treatment item data: {data}")
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)
    except Exception as e:
        logging.error(f"Error creating treatment: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )


# 시술 예약 목록 조회 서비스
def get_treatment_list_service(
    db: Session, current_shop: Shop, filters: TreatmentFilterParams
) -> Page[Treatment]:
    try:
        return get_treatment_list(db=db, shop_id=current_shop.id, filters=filters)
    except Exception:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )
