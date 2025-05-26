from datetime import timedelta

from fastapi import Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_SECONDS,
    SECRET_KEY,
)
from app.core.security import create_jwt_token, verify_password
from app.crud.user_crud import get_user_by_email, get_user_by_id
from app.exceptions import CustomException
from app.models.user import User
from app.schemas.auth import LoginResponse
from app.utils.redis.auth import (
    clear_refresh_token_redis,
    get_refresh_token_redis,
    get_refresh_token_ttl,
    set_refresh_token_redis,
)
from app.utils.redis.user import clear_user_redis

DOMAIN = "AUTH"


def authenticate_user_service(db: Session, email: str, password: str) -> User:
    """이메일과 비밀번호를 사용하여 사용자를 인증한다.

    - db: SQLAlchemy 세션 객체
    - email: 사용자 이메일
    - password: 사용자 비밀번호
    - 반환값: 인증된 사용자 객체
    - 예외: 인증 실패 시 CustomException 발생
    """
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
        )
    return user


def generate_tokens(user: User) -> LoginResponse:
    """유저 정보를 기반으로 액세스 토큰과 리프레시 토큰을 생성해서 반환한다.

    - 액세스 토큰: 만료 시간은 ACCESS_TOKEN_EXPIRE_SECONDS 초
    - 리프레시 토큰: 만료 시간은 REFRESH_TOKEN_EXPIRE_SECONDS 일
    """
    access_token = generate_access_token(user)  # 액세스 토큰 생성
    refresh_token = generate_refresh_token(user)  # 리프레시 토큰 생성
    set_refresh_token_redis(user.id, refresh_token)  # Redis에 리프레시 토큰 저장
    return access_token, refresh_token


def generate_access_token(user: User) -> str:
    """유저 정보를 기반으로 액세스 토큰(JWT)을 생성해서 반환한다.

    - sub: 유저 ID
    - role: 유저 권한(예: admin, user)
    - email: 유저 이메일
    - type: 'access' (액세스 토큰임을 명시)
    - 만료 시간: ACCESS_TOKEN_EXPIRE_SECONDS 초
    """
    return create_jwt_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "email": user.email,
            "type": "access",
        },
        expires_delta=timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS),
    )


def generate_refresh_token(user: User) -> str:
    """유저 정보를 기반으로 리프레시 토큰(JWT)을 생성해서 반환한다.

    - sub: 유저 ID
    - type: 'refresh' (리프레시 토큰임을 명시)
    - 만료 시간: REFRESH_TOKEN_EXPIRE_SECONDS 일
    """
    return create_jwt_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_SECONDS),
    )


def refresh_access_token(db: Session, request: Request) -> tuple[str, str]:
    """리프레시 토큰으로 액세스 토큰과(필요 시) 새로운 리프레시 토큰을 재발급한다.

    리프레시 토큰 만료 TTL이 절반 이하일 때만 새로 발급하고,
    절반 이상 남아있으면 기존 토큰을 그대로 반환한다.

    - request: FastAPI Request 객체
    - db: SQLAlchemy 세션 객체
    - 반환값: (액세스 토큰, 리프레시 토큰)
    - 예외: 리프레시 토큰이 없거나 유효하지 않은 경우
    """
    raw_token = request.headers.get("X-Refresh-Token") or request.cookies.get(
        "refresh_token",
    )
    if not raw_token:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="Refresh token not found",
            hint="헤더나 쿠키에 리프레시 토큰 확인해보슈",
        )
    try:
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError as e:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="Invalid refresh token",
            hint="리프레시 토큰이 유효하지 않으니 로그인으로 보내도록",
            exception=e,
        ) from e

    # Redis에서 리프레시 토큰 확인
    saved_token = get_refresh_token_redis(user_id)
    if not saved_token or saved_token != raw_token:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="Refresh token is invalid or expired.",
            hint="리프레시 토큰이 레디스에 없으니 로그인으로 보내도록",
        )

    # 남은 TTL 확인 (초 단위)
    ttl = get_refresh_token_ttl(user_id)
    half_ttl = ttl / 2 if ttl > 0 else -1

    # 유저 정보 조회
    user = get_user_by_id(db, user_id)
    if not user or user.is_deleted():
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="User not found",
        )

    # 리프레시 토큰 재발급 여부 결정
    if 0 < ttl <= half_ttl:
        # 남은 시간이 절반 이하라면 새 리프레시 토큰 발급
        new_access_token, new_refresh_token = generate_tokens(user)
        set_refresh_token_redis(new_refresh_token)  # Redis에 새 리프레시 토큰 저장
    else:
        # 아직 충분히 남았으면 기존 토큰 유지
        new_access_token = generate_access_token(user)
        new_refresh_token = raw_token

    return new_access_token, new_refresh_token


def logout_user(token: str | None) -> bool:
    """사용자 로그아웃 처리.

    - token: 리프레시 토큰 (없으면 False 반환)
    - 반환값: 성공 여부 (True/False)
    """
    if not token:
        return False
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        clear_refresh_token_redis(user_id)
        clear_user_redis(user_id)
    except JWTError:
        return False
    return True
