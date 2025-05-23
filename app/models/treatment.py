from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, Text, func, text
from sqlalchemy.orm import relationship

from app.enum.treatment_status import TreatmentStatus
from app.models.base import Base
from app.models.mixin.timestamp import TimestampMixin


class Treatment(Base, TimestampMixin):
    __tablename__ = "treatment"
    __table_args__ = {"comment": "시술 예약 테이블"}

    id = Column(Integer, primary_key=True, index=True, comment="시술 예약 ID")
    shop_id = Column(
        Integer,
        ForeignKey("shop.id", ondelete="CASCADE"),
        nullable=False,
        comment="샵 ID",
    )
    phonebook_id = Column(
        Integer, ForeignKey("phonebook.id"), nullable=False, comment="시술 대상 고객 ID"
    )

    reserved_at = Column(DateTime, nullable=False, comment="예약 일시")
    memo = Column(Text, nullable=True, comment="메모")
    status = Column(
        SqlEnum(TreatmentStatus, name="treatment_status"),
        nullable=False,
        default=TreatmentStatus.RESERVED,
        comment="예약 상태",
    )

    finished_at = Column(DateTime, nullable=True, comment="시술 완료일시")

    # Relationships
    treatment_items = relationship(
        "TreatmentItem", back_populates="treatment", cascade="all, delete-orphan"
    )

    phonebook = relationship(
        "Phonebook",
        back_populates="treatments",
        foreign_keys=[phonebook_id],
    )

    shop = relationship("Shop", back_populates="treatments")
