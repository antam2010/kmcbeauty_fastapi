from sqlalchemy import Column, Integer, String
from app.model.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), nullable=False, unique=True, comment="유저 이메일")
    name = Column(String(50), nullable=False, comment="유저 이름")
    token = Column(String(100), nullable=True, comment="유저 토큰")
    password = Column(String(100), nullable=False)
