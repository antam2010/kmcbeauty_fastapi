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
    """대시보드 데이터 캐시 저장 (value는 dict 또는 Pydantic model)."""
    if hasattr(value, "model_dump"):
        # Pydantic v2 이상
        data = value.model_dump()
    elif hasattr(value, "dict"):
        # Pydantic v1
        data = value.dict()
    elif isinstance(value, list):
        # Pydantic model 리스트
        data = [v.model_dump() if hasattr(v, "model_dump") else v.dict() for v in value]
    else:
        data = value  # 이미 dict라면 그대로
    key = get_dashboard_cache_key(shop_id, field, period)
    redis_client.set(key, json.dumps(data), ex=ttl)


def get_dashboard_cache(shop_id: int, field: str, period: str) -> dict | list | None:
    """대시보드 데이터 캐시 조회 (존재하지 않으면 None)."""
    key = get_dashboard_cache_key(shop_id, field, period)
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None


def clear_dashboard_cache(shop_id: int, field: str, period: str) -> None:
    """대시보드 캐시 삭제(무효화)."""
    key = get_dashboard_cache_key(shop_id, field, period)
    redis_client.delete(key)
