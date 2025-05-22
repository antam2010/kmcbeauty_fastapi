import logging

from fastapi import status
from fastapi_pagination import Page
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.treatment import (
    create_treatment,
    create_treatment_item,
    delete_treatment_items,
    get_treatment_by_id,
    get_treatment_list,
    validate_menu_detail_exists,
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
    data: TreatmentCreate,
    db: Session,
    current_shop: Shop,
) -> TreatmentResponse:
    """시술 예약을 생성하는 서비스.

    :param data: TreatmentCreate 모델
    :param db: DB 세션
    :param current_shop: 현재 상점
    :return: TreatmentResponse 모델
    """
    try:
        # 1. 예약 생성
        treatment = Treatment(
            shop_id=current_shop.id,
            phonebook_id=data.phonebook_id,
            reserved_at=data.reserved_at,
            memo=data.memo,
            status=data.status,
            finished_at=data.finished_at,
        )
        create_treatment(db, treatment)

        # 2. 시술 항목 유효성 검사 및 생성
        for item in data.treatment_items:
            menu_detail = (
                db.query(TreatmentMenuDetail).filter_by(id=item.menu_detail_id).first()
            )
            if not menu_detail:
                raise CustomException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    domain=DOMAIN,
                    detail=f"시술 항목 ID {item.menu_detail_id}이 존재하지 않습니다.",
                )

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

    except CustomException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e


def update_treatment_service(
    db: Session,
    treatment_id: int,
    data: TreatmentCreate,
    current_shop: Shop,
) -> TreatmentResponse:
    """시술 예약을 수정하는 서비스.

    :param db: DB 세션
    :param treatment_id: 수정할 시술 예약 ID
    :param data: TreatmentCreate 모델
    :param current_shop: 현재 상점
    :return: TreatmentResponse 모델
    """
    # 1. 기존 예약 조회 및 소유 샵 확인
    treatment = get_treatment_by_id(db, treatment_id)
    if not treatment or treatment.shop_id != current_shop.id:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            domain=DOMAIN,
            detail="시술 예약을 찾을 수 없습니다.",
        )

    try:
        # 2. 예약 정보 수정
        treatment.phonebook_id = data.phonebook_id
        treatment.reserved_at = data.reserved_at
        treatment.status = data.status
        treatment.memo = data.memo
        treatment.finished_at = data.finished_at

        # 3. 기존 시술 항목 삭제
        delete_treatment_items(db, treatment_id)

        # 4. 새 항목 삽입
        for item in data.treatment_items:
            menu_detail = validate_menu_detail_exists(db, item.menu_detail_id)
            if not menu_detail:
                raise CustomException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    domain=DOMAIN,
                    detail=f"시술 항목 ID {item.menu_detail_id}이 존재하지 않습니다.",
                )

            treatment_item = TreatmentItem(
                treatment_id=treatment.id,
                menu_detail_id=item.menu_detail_id,
                base_price=item.base_price,
                duration_min=item.duration_min,
            )
            create_treatment_item(db, treatment_item)

        db.commit()
        db.refresh(treatment)
        return TreatmentResponse.model_validate(treatment)

    except CustomException:
        db.rollback()
        raise

    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e


# 시술 예약 목록 조회 서비스
def get_treatment_list_service(
    db: Session,
    current_shop: Shop,
    filters: TreatmentFilter,
) -> Page[TreatmentDetail]:
    try:
        return get_treatment_list(db=db, shop_id=current_shop.id, filters=filters)
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
        )
