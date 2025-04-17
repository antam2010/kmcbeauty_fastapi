from fastapi import status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
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
from app.models.user import User
from app.schemas.treatment_menu import (
    TreatmentMenuCreate,
    TreatmentMenuCreateResponse,
    TreatmentMenuDetailCreate,
    TreatmentMenuDetailResponse,
    TreatmentMenuListRequest,
)

DOMAIN = "TREATMENT_MENU"


# 시술 메뉴 생성 서비스
def create_treatment_menu_service(
    params: TreatmentMenuCreate, user_id: int, db: Session
) -> TreatmentMenuCreateResponse:
    return create_treatment_menu(db=db, name=params.name, user_id=user_id)


# 시술 메뉴 조회 서비스
def get_treatment_menus_service(
    db: Session,
    current_user: User,
    params: TreatmentMenuListRequest,
) -> Page[TreatmentMenu]:
    list = get_treatment_menus_by_user(db, user_id=current_user.id, name=params.name)
    return paginate(list)


# 시술 메뉴 상세 조회 서비스
def get_treatment_menu_detail_service(
    menu_id: int,
    user_id: int,
    db: Session,
) -> TreatmentMenuDetailResponse:
    result = get_treatment_menu_details_by_user(
        db=db,
        menu_id=menu_id,
        user_id=user_id,
    )
    return result


# 시술 메뉴 상세 항목 생성 서비스
def create_treatment_menu_detail_service(
    menu_id: int,
    user_id: int,
    params: TreatmentMenuDetailCreate,
    db: Session,
) -> TreatmentMenuDetail:

    menu = db.query(TreatmentMenu).filter(TreatmentMenu.id == menu_id).first()
    if not menu:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            domain=DOMAIN,
        )

    if menu.user_id != user_id:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            domain=DOMAIN,
        )

    if menu.deleted_at:
        raise CustomException(
            status_code=status.HTTP_400_BAD_REQUEST,
            domain=DOMAIN,
        )

    return create_treatment_menu_detail(
        db=db,
        menu_id=menu_id,
        name=params.name,
        duration_min=params.duration_min,
        base_price=params.base_price,
    )
