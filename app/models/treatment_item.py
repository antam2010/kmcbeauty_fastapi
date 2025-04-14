from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from app.models.base import Base


class TreatmentItem(Base):
    __tablename__ = "treatment_item"
    __table_args__ = {"comment": "시술 항목 테이블"}

    id = Column(Integer, primary_key=True, index=True, comment="시술 항목 ID")
    treatment_id = Column(
        Integer,
        ForeignKey("treatment.id", ondelete="CASCADE"),
        nullable=False,
        comment="시술 예약 ID",
    )
    menu_detail_id = Column(
        Integer,
        ForeignKey("treatment_menu_detail.id", ondelete="SET NULL"),
        nullable=True,
        comment="시술 상세 ID",
    )

    base_price = Column(
        Integer, nullable=False, server_default="0", comment="기본 가격"
    )

    duration_min = Column(
        Integer, nullable=False, server_default="0", comment="소요 시간 (분)"
    )

    created_at = Column(DateTime, server_default=func.now(), comment="생성일시")

    # 이 항목이 속한 시술 예약 객체와의 관계 (N:1)
    # Treatment.items 와 양방향 연결됨
    treatment = relationship("Treatment", back_populates="items")

    menu_detail = relationship("TreatmentMenuDetail", back_populates="items")
