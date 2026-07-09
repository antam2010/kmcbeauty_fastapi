from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.models.shop import Shop
from app.schemas.shop import ShopCreate

# 소유권 미검증 헬퍼 get_shop_by_id 는 호출부 0건의 미사용 코드였으며,
# 향후 shop-scoped 접근에서 소유권 없는 조회 경로로 오용될 위험이 있어 제거했다
# (SPEC-SECURITY-001 REQ-SEC-003, 죽은 코드 심층방어 하드닝).
# 샵 범위 접근은 소유권을 검증하는 get_user_shop_by_id 만 사용한다.


# @MX:NOTE: [AUTO] 활성 샵 조회 불변식 — 소프트삭제된 샵(deleted_at IS NOT NULL)은
#            목록/단건 조회에서 제외한다. (SPEC-FIX-001 REQ-FIX-001)


# 유저가 가진 특정 샵 조회 (소프트삭제 제외)
def get_user_shop_by_id(db: Session, user_id: int, shop_id: int) -> Shop | None:
    return (
        db.query(Shop)
        .filter(
            Shop.id == shop_id,
            Shop.user_id == user_id,
            Shop.deleted_at.is_(None),
        )
        .first()
    )


# 유저가 가진 모든 샵 조회 (소프트삭제 제외)
def get_user_shops(db: Session, user_id: int) -> Page[Shop]:
    query = (
        db.query(Shop)
        .filter(Shop.user_id == user_id, Shop.deleted_at.is_(None))
        .order_by(Shop.id.desc())
    )
    return paginate(query)


# 샵 생성
def create_shop(db: Session, shop_data: ShopCreate, user_id: int) -> Shop:
    shop = Shop(**shop_data.model_dump())
    shop.user_id = user_id
    db.add(shop)
    db.flush()
    return shop
