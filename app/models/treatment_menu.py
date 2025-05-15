from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.mixin.soft_delete import SoftDeleteMixin
from app.models.mixin.timestamp import TimestampMixin


class TreatmentMenu(Base, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "treatment_menu"
    __table_args__ = (
        UniqueConstraint("shop_id", "name", name="uq_treatment_menu_shop_id_name"),
        {"comment": "시술 메뉴 대분류 테이블"},
    )

    id = Column(Integer, primary_key=True, index=True, comment="시술 메뉴 대분류 ID")

    shop_id = Column(
        Integer,
        ForeignKey("shop.id", ondelete="CASCADE"),
        nullable=False,
        comment="샵 ID",
    )

    name = Column(String(255), nullable=False, comment="시술 대분류명")

    # 관계 정의
    shop = relationship("Shop", backref="treatment_menus")

    details = relationship(
        "TreatmentMenuDetail",
        back_populates="menu",
        cascade="all, delete-orphan",
    )
