from sqlalchemy.orm import Session

from app.models.shop_user import ShopUser


# 조회
def get_shop_user(db: Session, shop_id: int, user_id: int) -> ShopUser:
    return db.query(ShopUser).filter_by(shop_id=shop_id, user_id=user_id).first()


# 등록
def create_shop_user(db: Session, shop_user_data: ShopUser) -> ShopUser:
    db.add(shop_user_data)
    db.flush()
    return shop_user_data
