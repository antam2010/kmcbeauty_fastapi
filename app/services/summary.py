import logging
from calendar import monthrange
from collections.abc import Callable, Iterable, Mapping
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

    # ---- 유틸: 이터러블/Row/직렬화 보조 ----
    def _is_iterable_but_not_str(x: object) -> bool:
        return isinstance(x, Iterable) and not isinstance(x, (str, bytes, bytearray))

    def _row_to_plain(x: object):
        """SQLAlchemy Row 지원: Row -> dict, 그 외는 그대로."""
        if hasattr(x, "_mapping"):  # sqlalchemy.engine.Row
            return dict(x._mapping)
        return x

    def _to_cacheable(obj: object):
        """캐시에 넣을 때: Pydantic 모델이면 model_dump(), Row면 dict, 리스트는 원소별 처리."""
        if isinstance(obj, list):
            out = []
            for it in obj:
                if hasattr(it, "model_dump"):
                    out.append(it.model_dump(mode="json"))
                else:
                    out.append(_row_to_plain(it))
            return out
        if hasattr(obj, "model_dump"):
            return obj.model_dump(mode="json")
        return _row_to_plain(obj)

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
            # 캐시 히트: 모델로 복원
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

        # 1) 원본 취득
        raw = get_func()

        # 2) 반환형 '확정' (제너레이터/Row/tuple(items) 등 방어)
        if pydantic_model:
            # (a) Mapping -> 단일 모델
            if isinstance(raw, Mapping):
                result_obj: list[T] | T = pydantic_model.model_validate(dict(raw))

            # (b) 이터러블 계열 -> 리스트로 확정
            elif _is_iterable_but_not_str(raw):
                seq = list(raw)  # 제너레이터 소모 방지

                # dict.items() 같은 (key, value) 튜플 나열이면 단일 dict로 합쳐서 모델
                if seq and all(
                    isinstance(it, tuple) and len(it) == 2 and isinstance(it[0], str)
                    for it in seq
                ):
                    result_obj = pydantic_model.model_validate(dict(seq))

                # Row/Mapping 들의 리스트면 각 원소를 dict로 정규화 후 모델 리스트
                elif seq and isinstance(_row_to_plain(seq[0]), Mapping):
                    result_obj = [
                        pydantic_model.model_validate(dict(_row_to_plain(it)))
                        for it in seq
                    ]

                # 그 외엔 요소별로 그대로 모델링 시도
                else:
                    result_obj = [
                        pydantic_model.model_validate(_row_to_plain(it)) for it in seq
                    ]

            # (c) 단일 Row/스칼라
            else:
                raw2 = _row_to_plain(raw)
                if isinstance(raw2, Mapping):
                    result_obj = pydantic_model.model_validate(dict(raw2))
                else:
                    result_obj = pydantic_model.model_validate(raw2)
        # pydantic_model 없을 때도 제너레이터/Row는 확정
        elif _is_iterable_but_not_str(raw):
            result_obj = list(raw)
        else:
            result_obj = _row_to_plain(raw)

        # 3) 캐시에 넣기 (항상 직렬화된 형태)
        to_cache = _to_cacheable(result_obj)
        set_dashboard_cache(shop.id, field, period, to_cache)

        return result_obj

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
