from fastapi import Depends, status
from sqlalchemy.orm import Session

from app.crud.shop_crud import get_user_shop_by_id
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.exceptions import CustomException
from app.models.shop import Shop
from app.models.user import User
from app.utils.redis.shop import get_selected_shop_redis, set_selected_shop_redis


def get_current_shop(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Shop:
    shop_id = get_selected_shop_redis(user.id)
    if not shop_id:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="SHOP_NOT_SELECTED",
            hint="redis에 만료되거나 없음.",
        )

    shop = get_user_shop_by_id(db, user.id, shop_id)
    if not shop:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="SHOP_NOT_FOUND",
            hint="그런 상점 없습니다.",
        )
    set_selected_shop_redis(user.id, shop.id)
    return shop
