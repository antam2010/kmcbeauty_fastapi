from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import relationship

from app.enum.treatment_status import PaymentMethod, TreatmentStatus
from app.models.base import Base
from app.models.mixin.timestamp import TimestampMixin


class Treatment(Base, TimestampMixin):
    __tablename__ = "treatment"
    __table_args__ = ({"comment": "시술 예약 테이블"},)

    id = Column(Integer, primary_key=True, index=True, comment="시술 예약 ID")
    shop_id = Column(
        Integer,
        ForeignKey("shop.id", ondelete="CASCADE"),
        nullable=False,
        comment="샵 ID",
    )
    phonebook_id = Column(
        Integer,
        ForeignKey("phonebook.id"),
        nullable=False,
        comment="시술 대상 고객 ID",
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

    # New columns
    payment_method = Column(
        SqlEnum(PaymentMethod, name="payment_method"),
        nullable=False,
        default=PaymentMethod.CARD,
        comment="결제 수단",
    )
    staff_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="시술 담당자 유저 ID",
    )
    created_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="예약 생성자 유저 ID",
    )

    # Relationships
    treatment_items = relationship(
        "TreatmentItem",
        back_populates="treatment",
        cascade="all, delete-orphan",
    )

    phonebook = relationship(
        "Phonebook",
        back_populates="treatments",
        foreign_keys=[phonebook_id],
    )

    shop = relationship("Shop", back_populates="treatments", foreign_keys=[shop_id])

    staff_user = relationship(
        "User",
        foreign_keys=[staff_user_id],
        backref="treatments_as_staff",
    )

    created_user = relationship(
        "User",
        foreign_keys=[created_user_id],
        backref="treatments_created",
    )
