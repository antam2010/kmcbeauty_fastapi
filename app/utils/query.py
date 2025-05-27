from datetime import UTC, date, datetime, time, timezone

from sqlalchemy.orm import Query
from sqlalchemy.sql import ColumnElement

from app.utils.datetime import KST


def apply_date_range_filter(
    query: Query,
    field: ColumnElement,
    start_date: date | None,
    end_date: date | None,
    tz: timezone = KST,
) -> Query:
    """지정된 필드에 KST 날짜 기반 필터를 UTC로 변환하여 적용."""
    if start_date:
        start_dt = datetime.combine(start_date, time.min, tzinfo=tz).astimezone(UTC)
        query = query.filter(field >= start_dt)
    if end_date:
        end_dt = datetime.combine(end_date, time.max, tzinfo=tz).astimezone(UTC)
        query = query.filter(field <= end_dt)
    return query
