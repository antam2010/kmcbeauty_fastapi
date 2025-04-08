# app/services/user_service.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.crud.user import create_user, get_user_by_id, update_user_db
from app.model.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_if_authorized(db: Session, user_id: int, current_user: User) -> User:
    """
    user_id로 사용자 조회. 관리자 또는 본인만 접근 가능
    """
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(status_code=403)

    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404)

    return user


def update_user_if_authorized(
    db: Session, user_id: int, user_update: UserUpdate, current_user: User
) -> User:
    """
    user_id 기준 사용자 정보 수정 (본인 또는 관리자만)
    """
    user = get_user_if_authorized(db, user_id, current_user)

    user_data = user_update.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["password"] = hash_password(user_data["password"])

    return update_user_db(db, user, user_data)


def create_user_service(
    db: Session, user_create: UserCreate, current_user: User
) -> User:
    """
    사용자 생성: 관리자만 가능
    """
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403)

    return create_user(db, user_create)
