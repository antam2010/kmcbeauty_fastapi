import logging

from fastapi import status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.crud.user_crud import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_db,
)
from app.exceptions import CustomException
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserEmailCheckResponse,
    UserResponse,
    UserUpdate,
)
from app.utils.redis.user import clear_user_redis

DOMAIN = "USER"

ROLE_NAME_MAP = {
    "ADMIN": "관리자",
    "MASTER": "원장",
    "MANAGER": "매니저",
}


# 내 정보 조회
def get_user_service(db: Session, current_user: User) -> UserResponse:

    user_response = UserResponse.model_validate(current_user)
    user_response.role_name = ROLE_NAME_MAP.get(current_user.role, "Unknown")
    return user_response


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
        logging.exception(f"Error creating user: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN,
        )


# 회원 수정
def update_user_service(
    db: Session, user_update: UserUpdate, current_user: User,
) -> UserResponse:
    try:
        user = get_user_by_id(db, current_user.id)
        if not user:
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)

        user_data = user_update.model_dump(exclude_unset=True)

        # 비밀번호 해시 처리
        if user_data.get("password"):
            user_data["password"] = hash_password(user_data["password"])

        # 레디스 캐시 삭제
        clear_user_redis(user.id)

        # 사용자 정보 업데이트
        updated_user = update_user_db(db, user, user_data)
        user_response = UserResponse.model_validate(updated_user)
        user_response.role_name = ROLE_NAME_MAP.get(updated_user.role, "Unknown")
        return user_response

    except IntegrityError:
        raise CustomException(status_code=status.HTTP_409_CONFLICT, domain=DOMAIN)
    except CustomException as e:
        raise e
    except Exception as e:
        logging.exception(f"Error updating user: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN,
        )


def check_user_email_service(db: Session, email: str) -> UserEmailCheckResponse:
    """이메일 중복 체크 서비스
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
