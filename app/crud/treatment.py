from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.phonebook import Phonebook
from app.models.treatment import Treatment
from app.models.treatment_item import TreatmentItem
from app.schemas.treatment import TreatmentFilter


# 시술 예약 등록
def create_treatment(db: Session, treatment: Treatment) -> Treatment:
    db.add(treatment)
    db.flush()
    return treatment


# 시술 예약 항목 등록
def create_treatment_item(db: Session, treatment_item: TreatmentItem) -> TreatmentItem:
    db.add(treatment_item)
    db.flush()
    return treatment_item


# 시술 예약 목록 조회
def get_treatment_list(
    db: Session, shop_id: int, filters: TreatmentFilter
) -> Page[Treatment]:
    query = (
        db.query(Treatment)
        .options(
            joinedload(Treatment.treatment_items).joinedload(TreatmentItem.menu_detail),
            joinedload(Treatment.phonebook),
        )
        .filter(Treatment.shop_id == shop_id)
    )

    # 날짜 필터
    if filters.start_date:
        query = query.filter(Treatment.reserved_at >= filters.start_date)
    if filters.end_date:
        query = query.filter(Treatment.reserved_at <= filters.end_date)

    # 상태 필터
    if filters.status:
        query = query.filter(Treatment.status == filters.status)

    # 검색 필터
    if filters.search:
        keyword = f"%{filters.search}%"
        query = (
            query.join(Treatment.phonebook)
            .outerjoin(Treatment.treatment_items)
            .outerjoin(TreatmentItem.menu_detail)
        ).filter(
            or_(
                Phonebook.name.ilike(keyword),
                Phonebook.phone_number.ilike(keyword),
            )
        )

    # 정렬
    if filters.sort_by and hasattr(Treatment, filters.sort_by):
        sort_column = getattr(Treatment, filters.sort_by)
        sort_expr = getattr(sort_column, filters.sort_order, None)
        if sort_expr:
            query = query.order_by(sort_expr())

    return paginate(query)
