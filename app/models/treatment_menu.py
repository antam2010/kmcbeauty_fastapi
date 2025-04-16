from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, func,
                        text)
from sqlalchemy.orm import relationship

from app.models.base import Base


class TreatmentMenu(Base):
    __tablename__ = "treatment_menu"
    __table_args__ = {"comment": "시술 메뉴 대분류 테이블"}

    id = Column(Integer, primary_key=True, index=True, comment="시술 메뉴 대분류 ID")
    
    shop_id = Column(
        Integer,
        ForeignKey("shop.id", ondelete="CASCADE"),
        nullable=False,
        comment="샵 ID",
    )

    name = Column(String(255), nullable=False, comment="시술 대분류명")

    created_at = Column(DateTime, server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="수정일",
    )
    deleted_at = Column(DateTime, nullable=True, comment="삭제일시 (soft delete)")

    # 관계 정의
    shop = relationship("Shop", backref="treatment_menus")

    details = relationship(
        "TreatmentMenuDetail",
        back_populates="menu",
        cascade="all, delete-orphan",
    )
