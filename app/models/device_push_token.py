from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text

from app.models.base import Base
from app.models.mixin.timestamp import TimestampMixin


class DevicePushToken(Base, TimestampMixin):
    __tablename__ = "device_push_tokens"
    __table_args__ = ({"comment": "디바이스 푸시 토큰 테이블"},)

    id = Column(Integer, primary_key=True, comment="디바이스 푸시 토큰 ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="유저 ID",
    )
    shop_id = Column(
        Integer,
        ForeignKey("shop.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="샵 ID",
    )
    device_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="디바이스 고유 ID",
    )  # 디바이스 고유 id
    token = Column(
        Text,
        nullable=False,
        unique=True,
        index=True,
        comment="FCM 토큰",
    )  # FCM 토큰
    platform = Column(String(10), nullable=False, comment="플랫폼 (iOS/Android 등)")
    is_active = Column(
        Boolean,
        nullable=False,
        server_default="1",
        comment="활성화 여부",
    )
