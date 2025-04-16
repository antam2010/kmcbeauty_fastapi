from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.database import get_db
from app.models.shop import Shop
from app.models.user import User
from app.schemas.shop import ShopCreate, ShopResponse, ShopUpdate
from app.services.shop_service import (create_shop_service,
                                       get_my_shops_service,
                                       get_selected_shop_service,
                                       set_selected_shop_service,
                                       update_shop_service)

router = APIRouter(prefix="/shops", tags=["Shop"])

@router.get(
    "/",
    response_model=list[ShopResponse],
    summary="내 샵 목록 조회",
    description="로그인한 유저의 샵 목록을 조회합니다."
)
def get_my_shops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_my_shops_service(db=db, user=current_user)

@router.post(
    "/",
    response_model=ShopResponse,
    status_code=status.HTTP_201_CREATED,
    summary="샵 생성",
    description="새로운 샵을 생성합니다."
)
def create_shop(
    shop_data: ShopCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_shop_service(db=db, user=current_user, shop_data=shop_data)

@router.put(
    "/{shop_id}",
    response_model=ShopResponse,
    status_code=status.HTTP_200_OK,
    summary="샵 수정",
    description="샵 정보를 수정합니다."
)
def update_shop(
    shop_id: int,
    shop_data: ShopUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
  return update_shop_service(db=db, user=current_user, shop_id=shop_id, shop_data=shop_data)

@router.post(
    "/selected",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="선택한 샵 설정",
    description="현재 선택한 샵을 설정합니다."
)
def select_shop(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    return set_selected_shop_service(db=db, user=current_user, shop_id=shop_id)


@router.get(
    "/selected",
    response_model=ShopResponse,
    summary="선택한 샵 조회",
    description="현재 선택된 샵을 조회합니다.",
)
def get_selected_shop(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Shop:
    return get_selected_shop_service(db=db, user=current_user)