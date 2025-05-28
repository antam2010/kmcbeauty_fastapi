from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import case

from app.enum.treatment_status import PaymentMethod, TreatmentStatus
from app.models.treatment import Treatment
from app.models.treatment_item import TreatmentItem
from app.schemas.dashboard import TreatmentSummarySchema
from app.utils.query import apply_date_range_filter


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
