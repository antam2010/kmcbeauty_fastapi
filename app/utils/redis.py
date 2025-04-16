from app.core.redis_client import redis_client


def set_selected_shop_redis(user_id: int, shop_id: int):
    key = f"user:{user_id}:selected_shop"
    redis_client.set(key, shop_id, ex=60 * 60 * 2)


def get_selected_shop_redis(user_id: int) -> int | None:
    key = f"user:{user_id}:selected_shop"
    shop_id = redis_client.get(key)
    return int(shop_id) if shop_id else None

def clear_selected_shop_redis(user_id: int):
    key = f"user:{user_id}:selected_shop"
    redis_client.delete(key)
