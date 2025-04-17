import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.crud.user import create_user, get_user_by_email, update_user_db
from app.exceptions import CustomException
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserEmailCheckResponse,
    UserResponse,
    UserUpdate,
)

DOMAIN = "USER"


# 내 정보 조회
def get_user_service(db: Session, current_user: User) -> UserResponse:
    return current_user


# 회원 생성
def create_user_service(db: Session, user_create: UserCreate) -> UserResponse:
    user_data = user_create.model_dump()
    try:
        user_data["password"] = hash_password(user_create.password)
        return create_user(db, user_data)
    except IntegrityError:
        db.rollback()
        logging.warning(f"User with email {user_create.email} already exists.")
        raise CustomException(status_code=status.HTTP_409_CONFLICT, domain=DOMAIN)
    except Exception as e:
        db.rollback()
        logging.error(f"Error creating user: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )


# 회원 수정
def update_user_service(
    db: Session, user_update: UserUpdate, current_user: User
) -> UserResponse:
    try:
        # 현재 로그인한 유저 정보 조회
        user = get_user_service(db, current_user)

        user_data = user_update.model_dump(exclude_unset=True)

        # 비밀번호 해시 처리
        if user_data.get("password"):
            user_data["password"] = hash_password(user_data["password"])

        return update_user_db(db, user, user_data)
    except IntegrityError:
        raise CustomException(status_code=status.HTTP_409_CONFLICT, domain=DOMAIN)
    except Exception as e:
        logging.exception(f"Error updating user: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )


def check_user_email_service(db: Session, email: str) -> UserEmailCheckResponse:
    """
    이메일 중복 체크 서비스
    """
    exists = None
    message = None
    user = get_user_by_email(db, email=email)
    if user:
        exists = True
        message = "이미 존재하는 이메일입니다."
    else:
        exists = False
        message = "사용 가능한 이메일입니다."
    return UserEmailCheckResponse(exists=exists, message=message)
