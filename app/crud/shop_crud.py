from sqlalchemy.orm import Session

from app.models.shop import Shop
from app.schemas.shop import ShopCreate, ShopUpdate


# 단일 샵 조회
def get_shop_by_id(db: Session, shop_id: int) -> Shop | None:
    return db.query(Shop).filter(Shop.id == shop_id).first()


# 유저가 가진 특정 샵 조회
def get_user_shop_by_id(db: Session, user_id: int, shop_id: int) -> Shop | None:
    return db.query(Shop).filter(Shop.id == shop_id, Shop.user_id == user_id).first()


# 유저가 가진 모든 샵 조회
def get_user_shops(db: Session, user_id: int) -> list[Shop]:
    return (
        db.query(Shop)
        .filter(Shop.user_id == user_id)
        .order_by(Shop.created_at.desc())
        .all()
    )


# 샵 생성
def create_shop(db: Session, shop_data: ShopCreate, user_id: int) -> Shop:
    shop = Shop(**shop_data.model_dump())
    shop.user_id = user_id
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


# 샵 수정
def update_shop(db: Session, shop: Shop, shop_data: ShopUpdate) -> Shop:
    for field, value in shop_data.model_dump().items():
        setattr(shop, field, value)
    db.commit()
    db.refresh(shop)
    return shop
