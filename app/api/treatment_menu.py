from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.shop import get_current_shop
from app.models.user import User
from app.schemas.treatment_menu import (
    TreatmentMenuCreate,
    TreatmentMenuCreateResponse,
    TreatmentMenuDetailCreate,
    TreatmentMenuDetailResponse,
    TreatmentMenuListRequest,
    TreatmentMenuResponse,
)
from app.services.treatment_menu_service import (
    create_treatment_menu_detail_service,
    create_treatment_menu_service,
    get_treatment_menu_detail_service,
    get_treatment_menus_service,
)

router = APIRouter(prefix="/treatment-menus", tags=["시술 메뉴"])


@router.get(
    "/",
    response_model=Page[TreatmentMenuResponse],
    summary="시술 메뉴 목록 조회",
    description="시술 메뉴 목록을 조회합니다.",
    status_code=status.HTTP_200_OK,
)
def get_menus(
    params: TreatmentMenuListRequest = Depends(),
    db: Session = Depends(get_db),
    current_shop=Depends(get_current_shop),
    
) -> Page[TreatmentMenuResponse]:
    return get_treatment_menus_service(
        db=db,
        current_shop=current_shop,
        params=params,
    )


@router.post(
    "/",
    response_model=TreatmentMenuCreateResponse,
    summary="시술 메뉴 생성",
    description="시술 메뉴를 생성합니다.",
    status_code=status.HTTP_201_CREATED,
)
def create_menu(
    params: TreatmentMenuCreate,
    db: Session = Depends(get_db),
    current_shop=Depends(get_current_shop),
) -> TreatmentMenuCreateResponse:
    return create_treatment_menu_service(
        db=db,
        params=params, 
        current_shop=current_shop, 
    )


# 시술 메뉴 상세 조회
@router.get(
    "/{menu_id}/details",
    response_model=list[TreatmentMenuDetailResponse],
    summary="시술 메뉴 상세 조회",
    description="시술 메뉴 상세를 조회합니다.",
)
def get_menu_detail(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TreatmentMenuDetailResponse]:
    return get_treatment_menu_detail_service(
        menu_id=menu_id,
        user_id=current_user.id,
        db=db,
    )


# 시술 메뉴 상세 생성
@router.post(
    "/{menu_id}/details",
    response_model=TreatmentMenuDetailResponse,
    summary="시술 메뉴 상세 생성",
    description="시술 메뉴 상세를 생성합니다.",
)
def create_menu_detail(
    menu_id: int,
    params: TreatmentMenuDetailCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_treatment_menu_detail_service(
        menu_id=menu_id,
        user_id=current_user.id,
        params=params,
        db=db,
    )
