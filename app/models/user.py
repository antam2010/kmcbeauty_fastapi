from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer, String, func, text
from sqlalchemy.orm import relationship

from app.enum.role import UserRole
from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "유저 테이블"}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), nullable=False, unique=True, comment="유저 이메일")
    name = Column(String(50), nullable=False, comment="유저 이름")
    password = Column(String(255), nullable=False, comment="비밀번호")
    token = Column(String(255), nullable=True, comment="유저 토큰")

    role = Column(
        SqlEnum(UserRole),
        nullable=False,
        server_default=UserRole.MASTER,
        comment="유저 권한",
    )

    created_at = Column(DateTime, server_default=func.now(), comment="생성일")
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="수정일",
    )

    # ✅ 관계 정의
    # User → Phonebook (1:N)
    # 해당 유저가 소유한 전화번호부 리스트
    phonebook_list = relationship(
        "Phonebook", back_populates="user", cascade="all, delete-orphan"
    )
