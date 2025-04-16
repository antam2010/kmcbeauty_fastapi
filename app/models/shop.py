from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, func,
                        text)
from sqlalchemy.orm import relationship

from app.models.base import Base


class Shop(Base):
    __tablename__ = "shop"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False, comment="샵 이름")
    address = Column(String(255), nullable=False, comment="샵 주소")
    address_detail = Column(String(255), comment="샵 상세 주소")
    phone = Column(String(20), comment="샵 전화번호")
    business_number = Column(String(20), comment="사업자 등록 번호")
    created_at = Column(DateTime, server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="수정일",
    )
    deleted_at = Column(DateTime, comment="삭제일시")

    # 관계 정의

    # Shop → Phonebook (1:N)
    phonebook_list = relationship(
        "Phonebook", back_populates="shop", cascade="all, delete-orphan"
    )
    # 이 샵의 소유자와의 관계 (N:1)
    owner = relationship("User", back_populates="shops")
    
    # Shop → Treatment (1:N)
    treatments = relationship(
        "Treatment", back_populates="shop", cascade="all, delete-orphan"
    )
