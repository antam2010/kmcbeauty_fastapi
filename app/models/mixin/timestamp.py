from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declared_attr


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        comment="생성일시",
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
        server_onupdate=func.now(),
        comment="수정일시",
    )

    @declared_attr.directive
    def __mapper_args__(cls):
        return {"eager_defaults": True}
