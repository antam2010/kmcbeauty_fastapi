from calendar import monthrange
from datetime import date

from sqlalchemy.orm import Session

from app.crud.treatment_crud import get_treatment_summary
from app.models.shop import Shop
from app.schemas.dashboard import (
    DashboardFilter,
    DashboardSummary,
    DashboardSummaryResponse,
)


def get_dashboard_summary_service(
    db: Session,
    shop: Shop,
    params: DashboardFilter,
) -> dict:
    treatment_target_summary = get_treatment_summary(
        db,
        shop.id,
        start_date=params.target_date,
        end_date=params.target_date,
    )
    treatment_month_summary = get_treatment_summary(
        db,
        shop.id,
        start_date=params.target_date.replace(day=1),
        end_date=date(
            params.target_date.year,
            params.target_date.month,
            monthrange(params.target_date.year, params.target_date.month)[1],
        ),
    )

    return DashboardSummaryResponse(
        target_date=params.target_date,
        summary=DashboardSummary(
            target_date=treatment_target_summary,
            month=treatment_month_summary,
        ),
    ).model_dump()
