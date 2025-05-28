from datetime import date

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import case

from app.enum.treatment_status import PaymentMethod, TreatmentStatus
from app.models.phonebook import Phonebook
from app.models.treatment import Treatment
from app.models.treatment_item import TreatmentItem
from app.models.treatment_menu_detail import TreatmentMenuDetail
from app.schemas.dashboard import TreatmentSummarySchema
from app.schemas.treatment import TreatmentAutoComplete, TreatmentFilter
from app.utils.query import apply_date_range_filter


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
    # WHERE treatment.reserved_at >= '2025-05-24 15:00:00.000000'
    #   AND treatment.reserved_at <= '2025-05-27 14:59:59.999999'
    stmt = apply_date_range_filter(
        stmt,
        Treatment.reserved_at,
        filters.start_date,
        filters.end_date,
    )

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


def get_treatment_summary(
    db: Session,
    shop_id: int,
    start_date: date,
    end_date: date,
) -> TreatmentSummarySchema:
    # 집계용 결제/상태 구분
    unpaid_methods = PaymentMethod.unpaid_methods()
    paid_methods = PaymentMethod.paid_methods()
    expected_statuses = TreatmentStatus.for_expected_sales()
    completed_status = TreatmentStatus.for_actual_sales()

    # group by 상태+결제방식
    stmt = (
        select(
            Treatment.status,
            Treatment.payment_method,
            func.count(Treatment.id).label("count"),
            func.sum(TreatmentItem.base_price).label("total_price"),
            func.sum(
                case(
                    # case 구문에서 unpaid_methods 리스트 직접 비교
                    (
                        Treatment.payment_method.in_(unpaid_methods),
                        TreatmentItem.base_price,
                    ),
                    else_=0,
                ),
            ).label("unpaid_total"),
        )
        .join(TreatmentItem, TreatmentItem.treatment_id == Treatment.id)
        .where(Treatment.shop_id == shop_id)
    )
    stmt = apply_date_range_filter(stmt, Treatment.reserved_at, start_date, end_date)
    stmt = stmt.group_by(Treatment.status, Treatment.payment_method)

    results = db.execute(stmt).fetchall()

    # 딕셔너리 가공
    count_map = {}
    sales_map = {}
    status_count = {}
    status_sales = {}

    for row in results:
        key = (row.status, row.payment_method)
        count_map[key] = row.count
        sales_map[key] = int(row.total_price or 0)
        status_count[row.status] = status_count.get(row.status, 0) + row.count
        status_sales[row.status] = status_sales.get(row.status, 0) + int(
            row.total_price or 0,
        )

    # 전체 예약 건수 (노쇼/취소 포함)
    total_reservations = sum(status_count.values())

    # 예상매출: RESERVED, VISITED, COMPLETED만 합산 (enum 메서드 사용)
    expected_sales = sum(status_sales.get(st, 0) for st in expected_statuses)

    # 실매출: COMPLETED 결제완료(카드/현금)
    actual_sales = sum(
        sales_map.get((completed_status, pay), 0) for pay in paid_methods
    )

    # 외상 합계: COMPLETED + 미수금(외상)
    unpaid_total = sum(
        sales_map.get((completed_status, pay), 0) for pay in unpaid_methods
    )
    return TreatmentSummarySchema(
        total_reservations=total_reservations,
        completed=status_count.get(TreatmentStatus.COMPLETED.value, 0),
        reserved=status_count.get(TreatmentStatus.RESERVED.value, 0),
        visited=status_count.get(TreatmentStatus.VISITED.value, 0),
        canceled=status_count.get(TreatmentStatus.CANCELLED.value, 0),
        no_show=status_count.get(TreatmentStatus.NO_SHOW.value, 0),
        expected_sales=expected_sales,
        actual_sales=actual_sales,
        unpaid_total=unpaid_total,
    )
