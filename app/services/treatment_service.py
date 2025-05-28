from fastapi import status
from fastapi_pagination import Page
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.treatment_crud import (
    create_treatment,
    get_treatment_by_id,
    get_treatment_items_by_treatment_id,
    get_treatment_list,
    validate_menu_detail_exists,
)
from app.exceptions import CustomException
from app.models.shop import Shop
from app.models.treatment import Treatment
from app.models.treatment_item import TreatmentItem
from app.schemas.treatment import (
    TreatmentCreate,
    TreatmentFilter,
    TreatmentResponse,
    TreatmentUpdate,
)

DOMAIN = "TREATMENT"


def get_treatment_list_service(
    db: Session,
    current_shop: Shop,
    filters: TreatmentFilter,
) -> Page[TreatmentResponse]:
    """시술 예약 목록을 조회하는 서비스.

    :param db: DB 세션
    :param current_shop: 현재 상점
    :param filters: TreatmentFilter 모델
    :return: Treatment 모델
    """
    try:
        return get_treatment_list(
            db=db,
            shop_id=current_shop.id,
            filters=filters,
        )

    except SQLAlchemyError as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            detail="DB Error",
            exception=e,
        ) from e
    except Exception as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            detail="Unknown Error",
            exception=e,
        ) from e


def upsert_treatment_service(
    db: Session,
    data: TreatmentCreate | TreatmentUpdate,
    current_shop: Shop,
    treatment_id: int | None = None,
) -> TreatmentResponse:
    """시술 예약을 생성 또는 수정하는 서비스.

    :param db: DB 세션
    :param data: TreatmentCreate 또는 TreatmentUpdate 모델
    :param current_shop: 현재 상점
    :param treatment_id: 수정할 시술 예약 ID
    :return: Treatment 모델
    """
    print(data)
    try:
        if treatment_id is None:
            # 생성 로직
            treatment = Treatment(
                shop_id=current_shop.id,
                phonebook_id=data.phonebook_id,
                reserved_at=data.reserved_at,
                memo=data.memo,
                status=data.status,
                finished_at=data.finished_at,
                staff_user_id=data.staff_user_id,
                created_user_id=current_shop.user_id,
            )
            treatment = create_treatment(db, treatment)
        else:
            # 수정 로직
            treatment = get_treatment_by_id(db, treatment_id)
            if not treatment or treatment.shop_id != current_shop.id:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    domain=DOMAIN,
                    detail="시술 예약을 찾을 수 없습니다.",
                )
            # 기존 예약 정보 수정
            treatment.phonebook_id = data.phonebook_id
            treatment.reserved_at = data.reserved_at
            treatment.status = data.status
            treatment.memo = data.memo
            treatment.finished_at = data.finished_at
            treatment.staff_user_id = data.staff_user_id

        # 시술 항목 upsert 처리
        existing_items = get_treatment_items_by_treatment_id(db, treatment.id)
        existing_items_map = {item.id: item for item in existing_items}
        received_ids = set()

        for item in data.treatment_items:
            menu_detail = validate_menu_detail_exists(db, item.menu_detail_id)
            if not menu_detail:
                raise CustomException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    domain=DOMAIN,
                    detail=f"시술 항목 ID {item.menu_detail_id}이 존재하지 않습니다.",
                )

            if getattr(item, "id", None) and item.id in existing_items_map:
                # update
                treatment_item = existing_items_map[item.id]
                treatment_item.menu_detail_id = item.menu_detail_id
                treatment_item.base_price = item.base_price
                treatment_item.duration_min = item.duration_min
                treatment_item.session_no = item.session_no
                received_ids.add(item.id)
            else:
                # insert
                new_item = TreatmentItem(
                    treatment_id=treatment.id,
                    menu_detail_id=item.menu_detail_id,
                    base_price=item.base_price,
                    duration_min=item.duration_min,
                    session_no=item.session_no,
                )
                db.add(new_item)

        # delete
        for existing_id, existing_item in existing_items_map.items():
            if existing_id not in received_ids:
                db.delete(existing_item)

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
