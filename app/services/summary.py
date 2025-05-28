from calendar import monthrange
from collections.abc import Callable
from datetime import date

from sqlalchemy.orm import Session

from app.crud.statistics_crud import (
    get_today_reservation_list_with_customer_insight,
    get_treatment_sales_summary,
    get_treatment_summary,
)
from app.models.shop import Shop
from app.schemas.dashboard import (
    DashboardFilter,
    DashboardSalesSummary,
    DashboardSummary,
    DashboardSummaryResponse,
)
from app.utils.redis.dashboard import (
    clear_dashboard_cache,
    get_dashboard_cache,
    set_dashboard_cache,
)


def get_dashboard_summary_service(
    db: Session,
    shop: Shop,
    params: DashboardFilter,
) -> DashboardSummaryResponse:
    target_date = params.target_date
    force_refresh = params.force_refresh

    month_start = target_date.replace(day=1)
    month_end = date(
        target_date.year,
        target_date.month,
        monthrange(target_date.year, target_date.month)[1],
    )

    # ---- 시술 요약 통계(오늘/월간) ----
    t_target_key = ("summary", target_date.isoformat())
    t_month_key = ("summary", month_start.isoformat())

    # ---- 시술별 매출(오늘/월간) ----
    s_target_key = ("sales", target_date.isoformat())
    s_month_key = ("sales", month_start.isoformat())

    # ---- 고객 인사이트 ----
    c_insight_key = ("customer_insight", target_date.isoformat())

    # ----- 공통 캐시 처리 -----
    def get_or_set_cache(
        key_tuple: tuple[str, str],
        get_func: Callable[[], dict],
    ) -> dict:
        field, period = key_tuple
        if force_refresh:
            # 캐시 무효화
            clear_dashboard_cache(shop.id, field, period)
        cached = get_dashboard_cache(shop.id, field, period)
        if cached and not force_refresh:
            return cached
        result = get_func()
        set_dashboard_cache(shop.id, field, period, result)
        return result

    # ---- 실제 데이터 획득 ----
    treatment_target_summary = get_or_set_cache(
        t_target_key,
        lambda: get_treatment_summary(
            db,
            shop.id,
            start_date=target_date,
            end_date=target_date,
        ),
    )
    treatment_month_summary = get_or_set_cache(
        t_month_key,
        lambda: get_treatment_summary(
            db,
            shop.id,
            start_date=month_start,
            end_date=month_end,
        ),
    )
    treatment_sales_target = get_or_set_cache(
        s_target_key,
        lambda: get_treatment_sales_summary(
            db,
            shop.id,
            start_date=target_date,
            end_date=target_date,
        ),
    )
    treatment_sales_month = get_or_set_cache(
        s_month_key,
        lambda: get_treatment_sales_summary(
            db,
            shop.id,
            start_date=month_start,
            end_date=month_end,
        ),
    )

    customer_insight = get_or_set_cache(
        c_insight_key,
        lambda: get_today_reservation_list_with_customer_insight(
            db,
            shop.id,
            start_date=target_date,
            end_date=target_date,
        ),
    )
    # ---- 통합 결과 리턴 ----
    return DashboardSummaryResponse(
        target_date=target_date,
        summary=DashboardSummary(
            target_date=treatment_target_summary,
            month=treatment_month_summary,
        ),
        sales=DashboardSalesSummary(
            target_date=treatment_sales_target,
            month=treatment_sales_month,
        ),
        customer_insights=customer_insight,
    ).model_dump()
