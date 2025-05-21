from datetime import UTC, datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declared_attr


class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True, comment="삭제일시")

    @declared_attr.directive
    def __mapper_args__(cls):
        return {"eager_defaults": True}

    def soft_delete(self):
        self.deleted_at = datetime.now(UTC)

    def is_deleted(self) -> bool:
        return self.deleted_at is not None
