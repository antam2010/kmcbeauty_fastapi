from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Phonebook(Base):
    __tablename__ = "phonebook"
    __table_args__ = (
        UniqueConstraint("shop_id", "phone_number", name="uq_shop_id_phone_number"),
        {"comment": "전화번호부 테이블"},
    )

    id = Column(Integer, primary_key=True, index=True, comment="전화번호 ID")
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

    created_at = Column(DateTime, server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="수정일",
    )

    # 관계 정의
    shop = relationship("Shop", back_populates="phonebook_list")
    treatments = relationship(
        "Treatment", back_populates="phonebook", cascade="all, delete-orphan"
    )
