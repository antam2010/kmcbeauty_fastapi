import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.crud.user import create_user, get_user_by_id, update_user_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


# 내 정보 조회
def get_user_service(db: Session, current_user: User) -> User:
    user = get_user_by_id(db, current_user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user


# 회원 생성
def create_user_service(db: Session, user_create: UserCreate) -> User:
    user_data = user_create.model_dump()
    try:
        user_data["password"] = hash_password(user_create.password)
        return create_user(db, user_data)
    except IntegrityError:
        db.rollback()
        logging.warning(f"User with email {user_create.email} already exists.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# 회원 수정
def update_user_service(
    db: Session, user_update: UserUpdate, current_user: User
) -> User:
    try:
        # 현재 로그인한 유저 정보 조회
        user = get_user_service(db, current_user)

        user_data = user_update.model_dump(exclude_unset=True)

        # 비밀번호 해시 처리
        if user_data.get("password"):
            user_data["password"] = hash_password(user_data["password"])

        return update_user_db(db, user, user_data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
