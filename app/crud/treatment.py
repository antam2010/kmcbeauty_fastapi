from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.enum.treatment_status import TreatmentStatus
from app.models.phonebook import Phonebook
from app.models.treatment import Treatment
from app.models.treatment_item import TreatmentItem
from app.models.treatment_menu_detail import TreatmentMenuDetail
from app.schemas.treatment import TreatmentAutoComplete, TreatmentFilter


# 시술 예약 등록
def create_treatment(db: Session, treatment: Treatment) -> Treatment:
    db.add(treatment)
    db.flush()
    return treatment


# 시술 예약 조회
def get_treatment_by_id(db: Session, treatment_id: int) -> Treatment | None:
    return db.query(Treatment).filter(Treatment.id == treatment_id).first()


# 시술 예약 항목 삭제
def delete_treatment_items(db: Session, treatment_id: int) -> None:
    db.query(TreatmentItem).filter(TreatmentItem.treatment_id == treatment_id).delete()


# 시술 예약 항목 등록
def create_treatment_item(db: Session, treatment_item: TreatmentItem) -> TreatmentItem:
    db.add(treatment_item)
    db.flush()
    return treatment_item


# 시술 예약 목록 조회
def get_treatment_list(
    db: Session,
    shop_id: int,
    filters: TreatmentFilter,
) -> Page[Treatment]:
    stmt = (
        select(Treatment)
        .options(
            joinedload(Treatment.treatment_items).joinedload(TreatmentItem.menu_detail),
            joinedload(Treatment.phonebook),
        )
        .where(Treatment.shop_id == shop_id)
    )

    # 날짜 필터
    if filters.start_date:
        stmt = stmt.where(Treatment.reserved_at >= filters.start_date)
    if filters.end_date:
        stmt = stmt.where(Treatment.reserved_at <= filters.end_date)

    # 상태 필터
    if filters.status:
        stmt = stmt.where(Treatment.status == filters.status)

    # 시술 담당자 필터
    if filters.staff_user_id:
        stmt = stmt.where(Treatment.staff_user_id == filters.staff_user_id)

    # 검색 필터
    if filters.search:
        keyword = f"%{filters.search}%"
        stmt = (
            stmt.join(Treatment.phonebook)
            .outerjoin(Treatment.treatment_items)
            .outerjoin(TreatmentItem.menu_detail)
            .where(
                or_(
                    Phonebook.name.ilike(keyword),
                    Phonebook.phone_number.ilike(keyword),
                ),
            )
        )

    # 정렬
    if filters.sort_by and hasattr(Treatment, filters.sort_by):
        sort_column = getattr(Treatment, filters.sort_by)
        sort_expr = getattr(sort_column, filters.sort_order, None)
        if sort_expr:
            stmt = stmt.order_by(sort_expr())

    # 실행 및 페이지네이션
    return paginate(db, stmt)


def validate_menu_detail_exists(
    db: Session,
    menu_detail_id: int,
) -> TreatmentMenuDetail | None:
    return db.query(TreatmentMenuDetail).filter_by(id=menu_detail_id).first()


def get_treatment_items_by_treatment_id(
    db: Session,
    treatment_id: int,
) -> list[TreatmentItem]:
    return (
        db.query(TreatmentItem).filter(TreatmentItem.treatment_id == treatment_id).all()
    )


def get_treatments_to_autocomplete(
    db: Session,
) -> list[TreatmentAutoComplete]:
    return (
        db.query(
            Treatment.id.label("treatment_id"),
            Treatment.reserved_at,
            func.sum(TreatmentItem.duration_min).label("total_duration_min"),
        )
        .join(TreatmentItem, TreatmentItem.treatment_id == Treatment.id)
        .filter(
            Treatment.status.in_(TreatmentStatus.unfinished_statuses()),
            Treatment.finished_at.is_(None),
        )
        .group_by(Treatment.id, Treatment.reserved_at)
        .limit(100)
        .all()
    )
