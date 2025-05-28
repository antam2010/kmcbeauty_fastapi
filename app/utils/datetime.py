from datetime import UTC, datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))


def now_kst() -> datetime:
    return datetime.now(KST)


def now_utc() -> datetime:
    return datetime.now(UTC)


def now_kst_today() -> datetime:
    return now_kst().date()
