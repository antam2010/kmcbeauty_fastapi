import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.shop_invite import ShopInvite


def create_invite(db: Session, shop_id: int) -> ShopInvite:
    invite_code = secrets.token_urlsafe(8)
    expired_at = datetime.now(UTC) + timedelta(days=7)

    invite = ShopInvite(
        shop_id=shop_id,
        invite_code=invite_code,
        expired_at=expired_at,
    )
    db.add(invite)
    db.flush()
    return invite


def get_invite_by_shop_id(
    db: Session,
    shop_id: int,
) -> ShopInvite | None:
    """샵 ID로 초대코드 조회.

    :param db: DB 세션
    :param shop_id: 샵 ID
    :return: 초대코드 정보
    """
    return db.query(ShopInvite).filter(ShopInvite.shop_id == shop_id).first()


def get_valid_invite_by_shop_id(db: Session, shop_id: int) -> ShopInvite | None:
    """샵 ID로 유효한 초대코드 조회.

    :param db: DB 세션
    :param shop_id: 샵 ID
    :return: 유효한 초대코드 정보
    """
    # 현재 시간보다 유효한 초대코드만 조회
    return (
        db.query(ShopInvite)
        .filter(
            ShopInvite.shop_id == shop_id,
            ShopInvite.expired_at > datetime.now(UTC),
        )
        .first()
    )


def delete_invite_by_shop_id(db: Session, shop_id: int) -> None:
    """샵 ID로 초대코드 삭제.

    :param db: DB 세션
    :param shop_id: 샵 ID
    """
    db.query(ShopInvite).filter(ShopInvite.shop_id == shop_id).delete()
    db.flush()
