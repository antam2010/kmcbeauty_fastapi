from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text

from app.models.base import Base
from app.models.mixin.timestamp import TimestampMixin


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True, comment="리프레시 토큰 ID")
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="사용자 ID",
    )
    token = Column(Text, nullable=False, comment="리프레시 토큰")
    expired_at = Column(DateTime, nullable=False, comment="만료일시")
