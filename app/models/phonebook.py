from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixin.soft_delete import SoftDeleteMixin
from app.models.mixin.timestamp import TimestampMixin


class Phonebook(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "phonebook"

    id = Column(Integer, primary_key=True, comment="전화번호 ID")

    shop_id = Column(
        Integer,
        ForeignKey("shop.id", ondelete="CASCADE"),
        nullable=False,
        comment="샵 ID",
    )

    group_name = Column(String(100), nullable=True, comment="그룹명 (선택)")
    name = Column(String(100), nullable=False, comment="이름")
    phone_number = Column(String(20), nullable=False, comment="전화번호")
    memo = Column(Text, nullable=True, comment="메모")

    # 관계 정의
    shop = relationship("Shop", back_populates="phonebook_list")
    treatments = relationship(
        "Treatment", back_populates="phonebook", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_shop_deleted_group", "shop_id", "deleted_at", "group_name"),
        Index("idx_shop_deleted_name", "shop_id", "deleted_at", "name"),
        Index("idx_shop_deleted_phone", "shop_id", "deleted_at", "phone_number"),
    )
