from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func, UniqueConstraint
from app.model.base import Base


class Phonebook(Base):
    __tablename__ = "phonebook"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    group_name = Column(String(100), nullable=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    memo = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "phone_number", name="uq_user_id_phone_number"),
    )
