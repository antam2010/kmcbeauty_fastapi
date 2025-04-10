from sqlalchemy import Column, DateTime, Enum as sqlEnum, Integer, String, func, text
from app.enum.role import UserRole
from app.model.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), nullable=False, unique=True, comment="유저 이메일")
    name = Column(String(50), nullable=False, comment="유저 이름")
    token = Column(String(100), nullable=True, comment="유저 토큰")
    password = Column(String(100), nullable=False)
    role = Column(
        sqlEnum(UserRole),
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
