from datetime import timedelta

from fastapi import Request, status
from jose import JWTError, jwt

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_SECONDS,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_SECONDS,
    SECRET_KEY,
)
from app.core.redis_client import redis_client
from app.core.security import create_jwt_token, verify_password
from app.crud.user_crud import get_user_by_email, get_user_by_id
from app.exceptions import CustomException
from app.models.user import User
from app.schemas.auth import LoginResponse

DOMAIN = "AUTH"


def authenticate_user_service(db, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
        )
    return user


def generate_tokens(user: User) -> LoginResponse:
    access_token = create_jwt_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "email": user.email,
            "type": "access",
        },
        expires_delta=timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS),
    )
    refresh_token = create_jwt_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_SECONDS),
    )
    # Redis에 리프레시 토큰 저장
    redis_client.setex(
        f"auth:refresh:{user.id}",
        REFRESH_TOKEN_EXPIRE_SECONDS,
        refresh_token,
    )
    return access_token, refresh_token


def refresh_access_token(db, request: Request) -> tuple[str, str]:
    raw_token = request.headers.get("X-Refresh-Token") or request.cookies.get(
        "refresh_token"
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
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
    except (JWTError, ValueError) as e:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="Invalid refresh token",
            hint="리프레시 토큰이 유효하지 않쇼",
            exception=e,
        )
    
    # Redis에서 리프레시 토큰 확인
    saved_token = redis_client.get(f"auth:refresh:{user_id}")
    if not saved_token or saved_token != raw_token:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="Refresh token is invalid or expired.",
            hint="리프레시 토큰이 레디스에 없거나 만료되었으니 로그인으로 보내도록",
        )
    
    # 유저 정보 조회
    user = get_user_by_id(db, user_id)
    if not user:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="User not found",
        )
    
    # 엑세스 토큰, 리프레시 토큰 재발급
    new_access_token, new_refresh_token = generate_tokens(user)
    return new_access_token, new_refresh_token


def logout_user(token: str | None) -> bool:
    try:
        if not token:
            return False
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        redis_client.delete(f"auth:refresh:{user_id}")
    except Exception:
        raise False
    return True
