from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixin.timestamp import TimestampMixin


class ShopInvite(Base, TimestampMixin):
    __tablename__ = "shop_invite"
    __table_args__ = (
        Index("idx_shop_invite_shop_id", "shop_id"),
        {"comment": "샵 초대코드 테이블"},
    )

    id = Column(Integer, primary_key=True, index=True, comment="초대코드 ID")
    shop_id = Column(
        Integer,
        ForeignKey("shop.id", ondelete="CASCADE"),
        nullable=False,
        comment="샵 ID",
    )
    invite_code = Column(String(20), unique=True, nullable=False, comment="초대코드")
    expired_at = Column(DateTime, nullable=False, comment="만료일시")

    shop = relationship("Shop", back_populates="invites")
