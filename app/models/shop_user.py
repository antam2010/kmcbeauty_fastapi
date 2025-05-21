from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class ShopUser(Base):
    __tablename__ = "shop_user"
    __table_args__ = (
        UniqueConstraint("shop_id", "user_id", name="uq_shop_user"),
        {"comment": "샵-유저 매핑 테이블"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="PK")
    shop_id = Column(
        Integer,
        ForeignKey("shop.id", ondelete="CASCADE"),
        nullable=False,
        comment="샵 ID",
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="유저 ID",
    )
    is_primary_owner = Column(
        Integer, nullable=False, default=0, comment="대표 원장 여부 (1=대표, 0=아님)"
    )
