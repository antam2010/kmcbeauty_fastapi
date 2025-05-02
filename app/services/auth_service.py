import logging
from datetime import timedelta, datetime, timezone
from fastapi import Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from cryptography.fernet import InvalidToken

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from app.core.security import create_access_token, verify_password, encrypt_token, decrypt_token
from app.exceptions import CustomException
from app.models.user import User
from app.models.refresh_token import RefreshToken

DOMAIN = "AUTH"


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
        )
    return user


def generate_tokens(
        db: Session,
        user: User
    ) -> tuple[str, str]:
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
    
    # DB 저장
    encrypted = encrypt_token(refresh_token)
    expired_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(user_id=user.id, token=encrypted, expired_at=expired_at))
    db.commit()

    return access_token, refresh_token


def refresh_access_token(request: Request, db: Session) -> str:
    # 쿠키에서 리프레시 토큰 꺼냄
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="Refresh token not found",
            hint="쿠키에 리프레시토큰이 없어"
            
        )

    # JWT 디코딩 시도
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "refresh":
            raise ValueError("Invalid token type")
    except (JWTError, ValueError):
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="Invalid refresh token",
            hint="리프레시 토큰이 유효하지 않아"
        )

    # DB에서 해당 리프레시 토큰 존재하는지 검증
    token_row = db.query(RefreshToken).filter(
        RefreshToken.user_id == int(user_id),
        RefreshToken.token == refresh_token,
        RefreshToken.expired_at > datetime.now(timezone.utc),
    ).first()

    # if not token_row:
    #     raise CustomException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         domain=DOMAIN,
    #         detail="Refresh token is not recognized",
    #         hint="리프레시 토큰이 DB에 존재하지 않아"
    #     )

    # # 유저 정보 조회
    # user = db.query(User).filter(User.id == int(user_id)).first()
    # if not user:
    #     raise CustomException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         domain=DOMAIN,
    #         detail="User not found",
    #         hint="유저 정보가 DB에 존재하지 않아"
    #     )

    # 새로운 액세스 토큰 발급
    new_access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "email": user.email,
            "type": "access"
        }
    )
    return new_access_token


def logout_user(db: Session, user_id: int, raw_token: str) -> bool:
    """
    해당 유저의 모든 리프레시 토큰 중
    raw_token 과 일치하는 한 건만 삭제 후 커밋.
    Returns:
        True  — 삭제 성공
        False — 매칭되는 토큰 없음
    """
    tokens = (
        db.query(RefreshToken)
          .filter(RefreshToken.user_id == user_id)
          .all()
    )

    target = None
    for token_obj in tokens:
        try:
            if decrypt_token(token_obj.token) == raw_token:
                target = token_obj
                break
        except InvalidToken:
            # 복호화가 불가능한 토큰(유효하지 않은 암호문)이면 패스
            continue

    if not target:
        return False  # 혹은 HTTPException(404) 로 던져도 좋습니다

    try:
        db.delete(target)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
        ) from e