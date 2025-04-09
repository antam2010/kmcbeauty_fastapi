from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.models.base import Base


class TreatmentMenuDetail(Base):
    __tablename__ = "treatment_menu_detail"
    __table_args__ = {"comment": "시술 메뉴 상세 테이블"}

    id = Column(Integer, primary_key=True, index=True, comment="시술 상세 ID")
    menu_id = Column(
        Integer,
        ForeignKey("treatment_menu.id", ondelete="CASCADE"),
        nullable=False,
        comment="시술 메뉴 대분류 ID",
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="유저 ID",
    )

    name = Column(String(255), nullable=False, comment="시술 항목명")
    duration_min = Column(Integer, nullable=False, comment="기본 시술 시간 (분)")
    base_price = Column(Integer, nullable=False, comment="기본 시술 가격 (원)")

    created_at = Column(DateTime, server_default=func.now(), comment="생성일시")
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="수정일시"
    )
    deleted_at = Column(DateTime, nullable=True, comment="삭제일시 (soft delete)")
