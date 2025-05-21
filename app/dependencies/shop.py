from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.shop import Shop
from app.utils.redis.shop import get_selected_shop_redis


def get_current_shop(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Shop:
    shop_id = get_selected_shop_redis(user.id)
    if not shop_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SHOP_NOT_SELECTED",
                "message": "상점이 선택되지 않았습니다.",
            },
        )

    shop = db.query(Shop).filter(Shop.id == shop_id, Shop.user_id == user.id).first()
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SHOP_NOT_FOUND", "message": "상점을 찾을 수 없습니다."},
        )

    return shop
