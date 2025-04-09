from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, Text, func
from sqlalchemy.orm import relationship

from app.enum.treatment_status import TreatmentStatus
from app.models.base import Base


class Treatment(Base):
    __tablename__ = "treatment"
    __table_args__ = {"comment": "시술 예약 테이블"}

    id = Column(Integer, primary_key=True, index=True, comment="시술 예약 ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="유저 ID",
    )
    phonebook_id = Column(
        Integer, ForeignKey("phonebook.id"), nullable=False, comment="시술 대상 고객 ID"
    )

    total_price = Column(Integer, nullable=False, comment="총 실제 시술 가격")
    reserved_at = Column(DateTime, nullable=False, comment="예약 일시")
    memo = Column(Text, nullable=True, comment="메모")
    status = Column(
        SqlEnum(TreatmentStatus, name="treatment_status"),
        nullable=False,
        default=TreatmentStatus.RESERVED,
        comment="예약 상태",
    )

    created_at = Column(DateTime, server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="수정일시"
    )
    finished_at = Column(DateTime, nullable=True, comment="시술 완료일시")

    # Relationships
    # Treatment → TreatmentItem (1:N 관계)
    # 시술 예약에 연결된 시술 항목 리스트
    # - back_populates: TreatmentItem.treatment 과 양방향 관계 설정
    # - cascade="all, delete-orphan":
    #     - 예약(Treatment)이 삭제되면 연결된 항목도 모두 삭제됨
    #     - 항목이 예약과의 관계에서 제거되면 (orphan) DB에서 자동 삭제됨
    items = relationship(
        "TreatmentItem", back_populates="treatment", cascade="all, delete-orphan"
    )

    # Treatment 모델
    phonebook = relationship(
        "Phonebook",
        back_populates="treatments",
        foreign_keys=[phonebook_id],
    )
