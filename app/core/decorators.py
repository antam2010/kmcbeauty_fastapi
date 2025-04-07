from functools import wraps

from fastapi import Depends, HTTPException, Request, status

from app.core.auth import get_current_user
from app.model.user import User


def role_required(roles: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args, current_user: User = Depends(get_current_user), **kwargs
        ):
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="접근 권한이 없습니다.",
                )
            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator


admin_required = role_required(["admin"])
