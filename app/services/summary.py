import logging
from calendar import monthrange
from collections.abc import Callable
from datetime import date
from typing import TypeVar

from sqlalchemy.orm import Session

from app.crud.statistics_crud import (
    get_staff_summary,
    get_today_reservation_list_with_customer_insight,
    get_treatment_sales_summary,
    get_treatment_summary,
)
from app.models.shop import Shop
from app.schemas.dashboard import (
    DashboardCustomerInsight,
    DashboardFilter,
    DashboardSalesSummary,
    DashboardStaffSummary,
    DashboardStaffSummaryItem,
    DashboardSummary,
    DashboardSummaryResponse,
    TreatmentSalesItem,
    TreatmentSummarySchema,
)
from app.utils.redis.dashboard import (
    clear_dashboard_cache,
    get_dashboard_cache,
    set_dashboard_cache,
)

T = TypeVar("T")


def get_dashboard_summary_service(
    db: Session,
    shop: Shop,
    params: DashboardFilter,
) -> dict:
    target_date = params.target_date
    force_refresh = params.force_refresh

    month_start = target_date.replace(day=1)
    month_end = date(
        target_date.year,
        target_date.month,
        monthrange(target_date.year, target_date.month)[1],
    )

    # ---- 캐시 키 정의 ----
    t_target_key = ("summary", target_date.isoformat())
    t_month_key = ("summary", month_start.isoformat())
    s_target_key = ("sales", target_date.isoformat())
    s_month_key = ("sales", month_start.isoformat())
    c_insight_key = ("customer_insight", target_date.isoformat())
    staff_target_key = ("staff_summary", target_date.isoformat())
    staff_month_key = ("staff_summary", month_start.isoformat())

    # ---- 공통 캐시 처리 함수 ----
    def get_or_set_cache(
        key_tuple: tuple[str, str],
        get_func: Callable[[], list[T] | T],
        pydantic_model: type[T] | None = None,
        force_refresh: bool = False,
    ) -> list[T] | T:
        field, period = key_tuple
        if force_refresh:
            clear_dashboard_cache(shop.id, field, period)

        cached = get_dashboard_cache(shop.id, field, period)
        if cached is not None and not force_refresh:
            if pydantic_model:
                if isinstance(cached, list):
                    logging.debug(
                        f"Cache hit for {field} on {period} for shop {shop.id} - multiple items",
                    )
                    return [pydantic_model.model_validate(v) for v in cached]
                logging.debug(
                    f"Cache hit for {field} on {period} for shop {shop.id} - single item",
                )
                return pydantic_model.model_validate(cached)
            logging.debug(
                f"Cache hit for {field} on {period} for shop {shop.id} - raw data",
            )
            return cached

        logging.debug(
            f"Cache miss for {field} on {period} for shop {shop.id}, fetching data...",
        )

        result = get_func()

        if isinstance(result, list):
            serialized = [
                r.model_dump(mode="json") if hasattr(r, "model_dump") else r
                for r in result
            ]
        else:
            serialized = (
                result.model_dump(mode="json")
                if hasattr(result, "model_dump")
                else result
            )

        set_dashboard_cache(shop.id, field, period, serialized)
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
        pydantic_model=TreatmentSummarySchema,
        force_refresh=force_refresh,
    )

    treatment_month_summary = get_or_set_cache(
        t_month_key,
        lambda: get_treatment_summary(
            db,
            shop.id,
            start_date=month_start,
            end_date=month_end,
        ),
        pydantic_model=TreatmentSummarySchema,
        force_refresh=force_refresh,
    )

    treatment_sales_target = get_or_set_cache(
        s_target_key,
        lambda: get_treatment_sales_summary(
            db,
            shop.id,
            start_date=target_date,
            end_date=target_date,
        ),
        pydantic_model=TreatmentSalesItem,
        force_refresh=force_refresh,
    )

    treatment_sales_month = get_or_set_cache(
        s_month_key,
        lambda: get_treatment_sales_summary(
            db,
            shop.id,
            start_date=month_start,
            end_date=month_end,
        ),
        pydantic_model=TreatmentSalesItem,
        force_refresh=force_refresh,
    )

    customer_insight = get_or_set_cache(
        c_insight_key,
        lambda: get_today_reservation_list_with_customer_insight(
            db,
            shop.id,
            start_date=target_date,
            end_date=target_date,
        ),
        pydantic_model=DashboardCustomerInsight,
        force_refresh=force_refresh,
    )

    staff_target_summary = get_or_set_cache(
        staff_target_key,
        lambda: get_staff_summary(
            db,
            shop.id,
            start_date=target_date,
            end_date=target_date,
        ),
        pydantic_model=DashboardStaffSummaryItem,
        force_refresh=force_refresh,
    )
    staff_month_summary = get_or_set_cache(
        staff_month_key,
        lambda: get_staff_summary(
            db,
            shop.id,
            start_date=month_start,
            end_date=month_end,
        ),
        pydantic_model=DashboardStaffSummaryItem,
        force_refresh=force_refresh,
    )

    # ---- 최종 결과 조립 후 리턴 ----
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
        staff_summary=DashboardStaffSummary(
            target_date=staff_target_summary,
            month=staff_month_summary,
        ),
    ).model_dump()
