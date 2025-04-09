from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.models.base import Base


class TreatmentMenu(Base):
    __tablename__ = "treatment_menu"
    __table_args__ = {"comment": "시술 메뉴 대분류 테이블"}

    id = Column(Integer, primary_key=True, index=True, comment="시술 메뉴 대분류 ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="유저 ID",
    )

    name = Column(String(255), nullable=False, comment="시술 대분류명")

    created_at = Column(DateTime, server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="수정일시"
    )
    deleted_at = Column(DateTime, nullable=True, comment="삭제일시 (soft delete)")
