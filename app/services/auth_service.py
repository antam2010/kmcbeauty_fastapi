from datetime import timedelta

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import (ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,
                             REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY)
from app.core.security import create_access_token, verify_password
from app.models.user import User


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )
    return user


def generate_tokens(user: User) -> tuple[str, str]:
    payload_base = {
        "sub": str(user.id),
        "role": user.role,
        "email": user.email,
    }

    access_token = create_access_token(
        data={**payload_base, "type": "access"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return access_token, refresh_token


def refresh_access_token(request: Request, db: Session) -> str:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="리프레시 토큰이 없습니다."
        )

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다.",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다."
        )

    new_access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "email": user.email,
            "type": "access",
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return new_access_token
