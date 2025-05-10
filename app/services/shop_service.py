import logging

from fastapi import status
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.crud.shop_crud import (
    create_shop,
    get_user_shop_by_id,
    get_user_shops,
    update_shop,
)
from app.exceptions import CustomException
from app.models.shop import Shop
from app.models.user import User
from app.schemas.shop import ShopCreate, ShopUpdate
from app.utils.redis.shop import (
    clear_selected_shop_redis,
    get_selected_shop_redis,
    set_selected_shop_redis,
)

DOMAIN = "SHOP"


# 샵 생성
def create_shop_service(db: Session, user: User, shop_data: ShopCreate) -> Shop:
    try:
        return create_shop(db, shop_data, user.id)
    except Exception as e:
        logging.exception(f"샵 생성 중 오류 발생: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )


# 샵 수정
def update_shop_service(
    db: Session, user: User, shop_id: int, shop_data: ShopUpdate
) -> Shop:
    try:
        shop = get_user_shop_by_id(db, user.id, shop_id)
        if not shop:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)

        return update_shop(db, shop, shop_data)

    except CustomException:
        raise
    except Exception as e:
        db.rollback()
        logging.exception(f"샵 수정 중 오류 발생: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )


# 샵 목록 조회
def get_my_shops_service(db: Session, user: User) -> Page[Shop]:
    try:
        return get_user_shops(db, user.id)
    except Exception as e:
        logging.exception(f"샵 목록 조회 중 오류 발생: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )


# 샵 선택
def set_selected_shop_service(db: Session, user: User, shop_id: int) -> None:
    try:
        shop = get_user_shop_by_id(db, user.id, shop_id)
        if not shop:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)

        set_selected_shop_redis(user.id, shop.id)

    except CustomException:
        raise
    except Exception as e:
        raise e


# 샵 선택 삭제
def delete_selected_shop_service(user: User) -> None:
    try:
        shop_id = get_selected_shop_redis(user.id)
        if not shop_id:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                domain=DOMAIN,
                code="SHOP_NOT_SELECTED",
            )

        clear_selected_shop_redis(user.id)

    except CustomException:
        raise
    except Exception as e:
        logging.exception(f"선택 샵 삭제 중 오류 발생: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )


# 샵 선택 조회
def get_selected_shop_service(db: Session, user: User) -> Shop:
    try:
        shop_id = get_selected_shop_redis(user.id)
        if not shop_id:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                domain=DOMAIN,
                code="SHOP_NOT_SELECTED",
            )

        shop = get_user_shop_by_id(db, user.id, shop_id)
        if not shop:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                domain=DOMAIN,
                code="SHOP_NOT_FOUND",
            )
        return shop
    except CustomException:
        raise
    except Exception as e:
        logging.exception(f"선택 샵 조회 중 오류 발생: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )
