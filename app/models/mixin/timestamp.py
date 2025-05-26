from typing import ClassVar

from sqlalchemy import Column, DateTime

from app.utils.datetime import now_kst


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=now_kst,
        comment="생성일시",
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=now_kst,
        onupdate=now_kst,
        comment="수정일시",
    )
    __mapper_args__: ClassVar[dict] = {"eager_defaults": True}
