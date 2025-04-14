from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.phonebook import Phonebook
from app.models.treatment import Treatment
from app.models.treatment_item import TreatmentItem
from app.models.treatment_menu_detail import TreatmentMenuDetail
from app.models.user import User
from app.schemas.treatment import TreatmentCreateRequest, TreatmentFilterParams


def create_treatment_with_items(
    db: Session, data: TreatmentCreateRequest, user: User
) -> Treatment:
    try:
        treatment = Treatment(
            user_id=user.id,
            phonebook_id=data.phonebook_id,
            reserved_at=data.reserved_at,
            memo=data.memo,
            total_price=data.total_price,
            status=data.status,
        )
        db.add(treatment)
        db.flush()

        for item in data.items:
            menu_detail = (
                db.query(TreatmentMenuDetail).filter_by(id=item.menu_detail_id).first()
            )
            if not menu_detail:
                raise ValueError(f"시술 항목 ID {item.menu_detail_id}이 존재하지 않음")

            db.add(
                TreatmentItem(
                    treatment_id=treatment.id,
                    menu_detail_id=menu_detail.id,
                    base_price=item.base_price,
                    duration_min=item.duration_min,
                )
            )

        db.commit()
        db.refresh(treatment)
        return treatment

    except Exception as e:
        db.rollback()
        raise e


# 시술 예약 목록 조회
def get_treatment_list(
    db: Session, user: User, filters: TreatmentFilterParams
) -> list[Treatment]:
    offset = (filters.page - 1) * filters.page_size

    query = (
        db.query(Treatment)
        .options(
            joinedload(Treatment.items).joinedload(TreatmentItem.menu_detail),
            joinedload(Treatment.phonebook),
        )
        .filter(Treatment.user_id == user.id)
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
            .outerjoin(Treatment.items)
            .outerjoin(TreatmentItem.menu_detail)
        )
        query = query.filter(
            or_(
                Phonebook.name.ilike(keyword),
                Phonebook.phone_number.ilike(keyword),
            )
        )

    # 정렬
    sort_column = getattr(Treatment, filters.sort_by)
    sort_expr = getattr(sort_column, filters.sort_order)()
    query = query.order_by(sort_expr)

    return query.offset(offset).limit(filters.page_size).all()
