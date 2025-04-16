import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.crud.shop_crud import create_shop, update_shop, get_user_shop_by_id, get_user_shops

from app.models.shop import Shop
from app.models.user import User

from app.schemas.shop import ShopCreate, ShopUpdate

from app.utils.redis import get_selected_shop_redis, set_selected_shop_redis

# 샵 생성
def create_shop_service(db: Session, user: User, shop_data: ShopCreate) -> Shop:
    try:
        return create_shop(db, shop_data, user.id)
    except Exception as e:
        logging.exception(f"샵 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 샵 수정
def update_shop_service(db: Session, user: User, shop_id: int, shop_data: ShopUpdate) -> Shop:
    try:
        shop = get_user_shop_by_id(db, user.id, shop_id)
        if not shop:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
        return update_shop(db, shop, shop_data)
     
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logging.exception(f"샵 수정 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 샵 목록 조회
def get_my_shops_service(db: Session, user: User) -> list[Shop]:
    try:
        return get_user_shops(db, user.id)
    except Exception as e:
        logging.exception(f"샵 목록 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 샵 선택
def set_selected_shop_service(db: Session, user: User, shop_id: int) -> None:
    try:
        shop = get_user_shop_by_id(db, user.id, shop_id)
        if not shop:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        
        set_selected_shop_redis(user.id, shop.id)

    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"선택 샵 설정 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 샵 선택 조회
def get_selected_shop_service(db: Session, user: User) -> Shop:
    try:
        shop_id = get_selected_shop_redis(user.id)
        if not shop_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_SELECTED")

        shop = get_user_shop_by_id(db, user.id, shop_id)
        if not shop:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
        return shop
    except HTTPException:
        raise
    except Exception as e:
        logging.exception(f"선택 샵 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
