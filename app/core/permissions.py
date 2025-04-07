from fastapi import HTTPException, status

from app.model.user import User


def require_role(current_user: User, allowed_roles: list[str]):
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다.",
        )


def is_self_or_admin(current_user: User, target_user_id: int):
    if current_user.id != target_user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인 또는 관리자만 접근할 수 있습니다.",
        )
