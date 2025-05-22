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
    db.commit()
    db.refresh(invite)
    return invite


def get_valid_invite(db: Session, invite_code: str) -> ShopInvite | None:
    return (
        db.query(ShopInvite)
        .filter(
            ShopInvite.invite_code == invite_code,
            ShopInvite.expired_at > datetime.now(UTC),
        )
        .first()
    )
