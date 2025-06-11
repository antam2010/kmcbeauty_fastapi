import json

from app.core.redis_client import redis_client

REDIS_PREFIX = "dashboard"
REDIS_TTL = 1800  # 30분


def get_dashboard_cache_key(shop_id: int, field: str, period: str) -> str:
    """Redis 키 생성 함수"""
    return f"{REDIS_PREFIX}:{shop_id}:{field}:{period}"


def set_dashboard_cache(
    shop_id: int,
    field: str,
    period: str,
    value: dict | list,
    ttl: int = REDIS_TTL,
) -> None:
    key = get_dashboard_cache_key(shop_id, field, period)
    serialized = json.dumps(value, ensure_ascii=False)
    redis_client.set(key, serialized, ex=ttl)


def get_dashboard_cache(shop_id: int, field: str, period: str) -> dict | list | None:
    key = get_dashboard_cache_key(shop_id, field, period)
    raw = redis_client.get(key)
    if raw is None:
        return None
    return json.loads(raw)


def clear_dashboard_cache(shop_id: int, field: str, period: str) -> None:
    key = get_dashboard_cache_key(shop_id, field, period)
    redis_client.delete(key)
