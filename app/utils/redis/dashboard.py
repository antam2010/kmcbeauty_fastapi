import json

from app.core.redis_client import redis_client

REDIS_PREFIX = "dashboard"
REDIS_TTL = 1800  # 30분 (1800초)


def get_dashboard_cache_key(shop_id: int, field: str, period: str) -> str:
    """대시보드용 Redis 캐시 키 생성.

    :param shop_id: 샵 ID
    :param field: 'summary' 또는 'sales'
    :param period: '2025-06-12' 또는 '2025-06' 등(일/월 단위)
    """
    return f"{REDIS_PREFIX}:{shop_id}:{field}:{period}"


def set_dashboard_cache(
    shop_id: int,
    field: str,
    period: str,
    value: dict | list,
    ttl: int = REDIS_TTL,
) -> None:
    key = get_dashboard_cache_key(shop_id, field, period)
    redis_client.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)


def get_dashboard_cache(shop_id: int, field: str, period: str) -> dict | list | None:
    key = get_dashboard_cache_key(shop_id, field, period)
    raw = redis_client.get(key)
    if not raw:
        return None
    return json.loads(raw)


def clear_dashboard_cache(shop_id: int, field: str, period: str) -> None:
    """대시보드 캐시 삭제(무효화)."""
    key = get_dashboard_cache_key(shop_id, field, period)
    redis_client.delete(key)
