import logging

from fastapi import status
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.crud.treatment import (
    create_treatment,
    create_treatment_item,
    get_treatment_list,
)
from app.exceptions import CustomException
from app.models.shop import Shop
from app.models.treatment import Treatment
from app.models.treatment_item import TreatmentItem
from app.models.treatment_menu_detail import TreatmentMenuDetail
from app.schemas.treatment import (
    TreatmentCreate,
    TreatmentDetail,
    TreatmentFilter,
    TreatmentResponse,
)

DOMAIN = "TREATMENT"


# 시술 예약 생성 서비스
def create_treatment_service(
    data: TreatmentCreate, db: Session, current_shop: Shop
) -> TreatmentResponse:

    try:
        treatment = Treatment(
            shop_id=current_shop.id,
            phonebook_id=data.phonebook_id,
            reserved_at=data.reserved_at,
            memo=data.memo,
            status=data.status,
            finished_at=data.finished_at,
        )
        create_treatment(db, treatment)

        for item in data.treatment_items:
            menu_detail = (
                db.query(TreatmentMenuDetail).filter_by(id=item.menu_detail_id).first()
            )
            if not menu_detail:
                raise ValueError(f"시술 항목 ID {item.menu_detail_id}이 존재하지 않음")

            treatment_item = TreatmentItem(
                treatment_id=treatment.id,
                menu_detail_id=menu_detail.id,
                base_price=item.base_price,
                duration_min=item.duration_min,
            )
            create_treatment_item(db, treatment_item)

        db.commit()
        db.refresh(treatment)
        return TreatmentResponse.model_validate(treatment)

    except ValueError as e:
        db.rollback()
        logging.exception(f"ValueError: {e}")
        raise CustomException(status_code=status.HTTP_400_BAD_REQUEST, domain=DOMAIN)
    except Exception as e:
        db.rollback()
        logging.exception(f"Unexpected error: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )


# 시술 예약 목록 조회 서비스
def get_treatment_list_service(
    db: Session, current_shop: Shop, filters: TreatmentFilter
) -> Page[TreatmentDetail]:
    try:
        return get_treatment_list(db=db, shop_id=current_shop.id, filters=filters)
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )
