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
    back_populates="menu",      # ❸ 반대편(TreatmentMenuDetail.menu)에서도 이 관계를 접근할 수 있게 연결
    cascade="all, delete-orphan",  # 부모 없는 상태면 삭제
    primaryjoin="and_("
    "TreatmentMenu.id==TreatmentMenuDetail.menu_id, "
    "TreatmentMenuDetail.deleted_at==None"
    ")"
)

