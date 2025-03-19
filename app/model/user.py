from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="유저 이름")
    token = Column(String(100), nullable=False, comment="유저 토큰")
    password = Column(String(100), nullable=False)
