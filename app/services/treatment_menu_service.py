import logging
from fastapi import status
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.crud.treatment_menu import (
    create_treatment_menu,
    create_treatment_menu_detail,
    get_treatment_menu_details_by_user,
    get_treatment_menus_by_user,
)
from app.exceptions import CustomException
from app.models.treatment_menu import TreatmentMenu
from app.models.treatment_menu_detail import TreatmentMenuDetail
from app.models.shop import Shop
from app.schemas.treatment_menu import (
    TreatmentMenuCreate,
    TreatmentMenuCreateResponse,
    TreatmentMenuDetailCreate,
    TreatmentMenuDetailResponse,
    TreatmentMenuFilter,
)

DOMAIN = "TREATMENT_MENU"


def get_treatment_menus_service(
    db: Session,
    current_shop: Shop,
    filters: TreatmentMenuFilter,
) -> Page[TreatmentMenu]:
    """
    시술 메뉴 목록 조회 서비스
    """
    list = get_treatment_menus_by_user(
        db=db, 
        shop_id=current_shop.id,
        search=filters.search
    )
    return list

# 시술 메뉴 생성 서비스
def create_treatment_menu_service(
    db: Session,
    current_shop: Shop,
    params: TreatmentMenuCreate, 
) -> TreatmentMenuCreateResponse:
    try:
        # 시술 메뉴 생성
        menu = create_treatment_menu(
            db=db, 
            name=params.name, 
            shop_id=current_shop.id
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logging.exception(f"SQLAlchemyError: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
        )
    db.refresh(menu)
    return menu


# 시술 메뉴 상세 조회 서비스
def get_treatment_menu_detail_service(
    menu_id: int,
    current_shop: Shop,
    db: Session,
) -> TreatmentMenuDetailResponse:
    result = get_treatment_menu_details_by_user(
        db=db,
        menu_id=menu_id,
        shop_id=current_shop.id,
    )
    return result


# 시술 메뉴 상세 항목 생성 서비스
def create_treatment_menu_detail_service(
    menu_id: int,
    current_shop: Shop,
    filters: TreatmentMenuDetailCreate,
    db: Session,
) -> TreatmentMenuDetail:

    menu = db.query(TreatmentMenu).filter(TreatmentMenu.id == menu_id).first()
    if not menu:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND,domain=DOMAIN,)

    if menu.shop_id != current_shop.id:
        raise CustomException(status_code=status.HTTP_403_FORBIDDEN,domain=DOMAIN,)

    if menu.deleted_at:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND,domain=DOMAIN)

    return create_treatment_menu_detail(
        db=db,
        menu_id=menu_id,
        name=filters.name,
        duration_min=filters.duration_min,
        base_price=filters.base_price,
    )
