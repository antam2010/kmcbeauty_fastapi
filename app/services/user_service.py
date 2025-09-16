from fastapi import status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.crud.shop_invite_curd import get_invite_by_code
from app.crud.shop_user_crud import ShopUser, create_shop_user
from app.crud.user_crud import (
    create_user,
    delete_user_db,
    get_user_by_email,
    get_user_by_id,
    update_user_db,
)
from app.enum.role import UserRole
from app.exceptions import CustomException
from app.models.shop_invite import ShopInvite
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserEmailCheckResponse,
    UserResponse,
    UserUpdate,
)
from app.utils.redis.auth import clear_refresh_token_redis

DOMAIN = "USER"


def get_user_service(db: Session, current_user: User) -> UserResponse:
    """현재 로그인한 사용자의 정보를 조회합니다."""
    user = get_user_by_id(db, current_user.id)
    if not user:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)

    return UserResponse.model_validate(user)


def validate_user_creation(data: UserCreate, db: Session) -> ShopInvite | None:
    if data.role == UserRole.ADMIN:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            domain=DOMAIN,
            hint="ADMIN 권한은 가입할 수 없습니다.",
        )

    invite = None
    if data.role == UserRole.MANAGER:
        if not data.invite_code:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST,
                domain=DOMAIN,
                detail="MANAGER 권한은 초대 코드가 필요합니다.",
            )

        invite = get_invite_by_code(db, data.invite_code)
        if not invite:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST,
                domain=DOMAIN,
                detail="유효하지 않거나 만료된 초대 코드입니다.",
            )
    return invite


# 회원 생성
def create_user_service(db: Session, user_create: UserCreate) -> UserResponse:
    role = user_create.role

    # 1. 유저 생성 유효성 검사
    invite = validate_user_creation(user_create, db)

    # 3. 유저 생성 준비
    user_data = user_create.model_dump(exclude={"invite_code"})
    user_data["password"] = hash_password(user_create.password)

    try:
        user = create_user(db, user_data)

        # 4. MANAGER라면 shop_user 등록
        if role == UserRole.MANAGER:
            shop_user_data = ShopUser(
                shop_id=invite.shop_id,
                user_id=user.id,
                is_primary_owner=0,
            )
            create_shop_user(
                db,
                shop_user_data,
            )

        db.commit()
        db.refresh(user)

    except IntegrityError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_409_CONFLICT,
            domain=DOMAIN,
            exception=e,
        ) from e
    except Exception as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e

    return UserResponse.model_validate(user)


# 회원 수정
def update_user_service(
    db: Session,
    user_update: UserUpdate,
    current_user: User,
) -> UserResponse:
    try:
        validate_user_creation(user_update, db)

        user = get_user_by_id(db, current_user.id)
        if not user or user.is_deleted():
            raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)

        user_data = user_update.model_dump(exclude_unset=True)

        # 비밀번호 해시 처리
        if user_data.get("password"):
            user_data["password"] = hash_password(user_data["password"])

        # 레디스 캐시 삭제
        clear_refresh_token_redis(user.id)

        # 사용자 정보 업데이트
        updated_user = update_user_db(db, user, user_data)
        return UserResponse.model_validate(updated_user)
    except IntegrityError as e:
        raise CustomException(
            status_code=status.HTTP_409_CONFLICT,
            domain=DOMAIN,
            exception=e,
        ) from e
    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e


def delete_user_service(
    db: Session,
    current_user: User,
    is_soft_delete: bool = False,
) -> None:
    """현재 로그인한 사용자를 삭제합니다."""
    user = get_user_by_id(db, current_user.id)
    if not user:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            domain=DOMAIN,
            hint="없슈.",
        )

    clear_refresh_token_redis(user.id)  # 레디스 캐시 삭제

    try:
        delete_user_db(
            db=db,
            user=user,
            is_soft_delete=is_soft_delete,
        )
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e


def check_user_email_service(db: Session, email: str) -> UserEmailCheckResponse:
    """이메일 중복 체크 서비스."""
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
