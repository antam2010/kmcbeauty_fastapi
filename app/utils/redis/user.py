import json
from typing import Any

from app.core.redis_client import redis_client
from app.models.user import User

REDIS_USER_PREFIX = "user"
REDIS_USER_TTL = 60 * 60 * 24  # 24시간


def _get_user_key(user_id: int) -> str:
    return f"{REDIS_USER_PREFIX}:{user_id}"


def get_user_redis(user_id: int) -> dict[str, Any] | None:
    """Redis에서 사용자 정보를 조회."""
    key = _get_user_key(user_id)
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def set_user_redis(user: User) -> None:
    """사용자 정보를 Redis에 저장."""
    key = _get_user_key(user.id)

    user_dict = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
    }

    redis_client.setex(key, REDIS_USER_TTL, json.dumps(user_dict))


def clear_user_redis(user_id: int) -> None:
    """사용자 정보를 Redis에서 삭제."""
    key = _get_user_key(user_id)
    redis_client.delete(key)
