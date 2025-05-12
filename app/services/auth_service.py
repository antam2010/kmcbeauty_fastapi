import logging
from datetime import datetime, timedelta, timezone

from cryptography.fernet import InvalidToken
from fastapi import Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)
from app.core.security import (
    create_access_token,
    decode_jwt_token,
    decrypt_token,
    encrypt_token,
    verify_password,
)
from app.exceptions import CustomException
from app.models.refresh_token import RefreshToken
from app.models.user import User

DOMAIN = "AUTH"


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
        )
    return user


def generate_tokens(db: Session, user: User) -> tuple[str, str]:
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


def refresh_access_token(
        request: Request, 
        db: Session
        ) -> tuple[str, str]:
    
    # 쿠키에서 리프레시 토큰 꺼냄
    refresh_token = request.headers.get("X-Refresh-Token") or request.cookies.get("refresh_token")
    if not refresh_token:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            detail="Refresh token not found",
            hint="쿠키에 리프레시토큰이 없어",
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
            hint="리프레시 토큰이 유효하지 않아",
        )

    # DB에서 해당 리프레시 토큰 존재하는지 검증
    rows = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == int(user_id),
            RefreshToken.expired_at > datetime.now(timezone.utc),
        )
        .all()
    )

    token_row = None
    for row in rows:
        try:
            # 복호화한 후, raw 토큰과 비교
            if decrypt_token(row.token) == refresh_token:
                token_row = row
                break
        except InvalidToken:
            continue

    if not token_row:
        logging.error(f"DB에 일치하는 리프레시 토큰이 없음 (user_id={user_id})")
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            code="REFRESH_NOT_FOUND",
            detail="리프레시 토큰이 DB에 존재하지 않습니다.",
            hint="다시 로그인하거나 지원팀에 문의하세요.",
        )

    # 유저 정보 조회
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            domain=DOMAIN,
            detail="User not found",
            hint="유저 정보가 DB에 존재하지 않아",
        )

    # 새로운 액세스 토큰 발급
    new_access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "email": user.email,
            "type": "access",
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return new_access_token, refresh_token


def logout_user(db: Session, raw_token: str) -> bool:
    try:
        payload = decode_jwt_token(raw_token)
        user_id = int(payload.get("sub"))

        tokens = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).all()

        target = None
        for token_obj in tokens:
            try:
                decrypted = decrypt_token(token_obj.token)
                if decrypted == raw_token:
                    target = token_obj
                    logging.debug(f"[LOGOUT] 매칭 토큰 발견 id={token_obj.id}")
                    break
            except InvalidToken:
                logging.warning(
                    f"[LOGOUT] 토큰(id={token_obj.id}) 복호화 실패: InvalidToken"
                )
            except Exception as e:
                logging.exception(
                    f"[LOGOUT] 토큰(id={token_obj.id}) 복호화 중 예외: {repr(e)}"
                )

        if not target:
            logging.info(f"[LOGOUT] 매칭되는 토큰 없음 user_id={user_id}")
            return False

        db.delete(target)
        db.commit()
        logging.info(f"[LOOUT] 토큰 삭제 성공 id={target.id}")
        return True

    except Exception as e:
        db.rollback()
        logging.exception(f"[LOGOUT] 예외 발생: {repr(e)}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            detail=f"토큰 삭제 중 서버 오류 발생: {repr(e)}",
            hint="백엔드 서버에 문의하세요.",
        ) from e
