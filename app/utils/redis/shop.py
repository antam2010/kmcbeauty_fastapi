from app.core.redis_client import redis_client

REDIS_SELECTED_SHOP_PREFIX = "user"
REDIS_SELECTED_SHOP_SUFFIX = "selected_shop"
REDIS_SELECTED_SHOP_TTL = 60 * 60 * 2  # 2시간


def _get_selected_shop_key(user_id: int) -> str:
    return f"{REDIS_SELECTED_SHOP_PREFIX}:{user_id}:{REDIS_SELECTED_SHOP_SUFFIX}"


def set_selected_shop_redis(user_id: int, shop_id: int) -> None:
    """
    Redis에 현재 선택된 shop_id 저장
    """
    key = _get_selected_shop_key(user_id)
    redis_client.set(key, shop_id, ex=REDIS_SELECTED_SHOP_TTL)


def get_selected_shop_redis(user_id: int) -> int | None:
    """
    Redis에서 선택된 shop_id 가져오기
    """
    key = _get_selected_shop_key(user_id)
    shop_id = redis_client.get(key)
    return int(shop_id) if shop_id else None


def clear_selected_shop_redis(user_id: int) -> None:
    """
    Redis에 저장된 선택 shop_id 삭제
    """
    key = _get_selected_shop_key(user_id)
    redis_client.delete(key)
