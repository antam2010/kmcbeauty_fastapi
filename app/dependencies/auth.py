import logging

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sentry_sdk import set_user
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET_KEY
from app.database import get_db
from app.exceptions import CustomException
from app.models.user import User
from app.utils.redis.user import get_user_redis, set_user_redis

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="not-used")



def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                domain="AUTH",
                hint="토큰 정보에 사용자 ID가 없습니다.",
            )
        
    except JWTError as e:
        logging.exception("JWTError: %s", e)
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain="AUTH",
            hint="토큰 정보가 유효하지 않습니다.",
        )

    except Exception as e:
        logging.exception("Exception: %s", e)
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain="AUTH",
            hint="서버 오류입니다.",
        )

    user_id = int(user_id)

    # Redis에서 사용자 캐시 조회
    cached_user = get_user_redis(user_id)
    if cached_user:
        # Sentry에 사용자 정보 설정
        set_user({"id": user_id, "email": cached_user["email"]})
        return User(**cached_user)

    # Redis에 없으면 DB에서 조회
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logging.exception("User not found: %s", user_id)
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain="AUTH",
            hint="사용자를 찾을 수 없습니다.",
        )

    # Sentry에 사용자 정보 설정
    set_user({"id": user.id, "email": user.email})

    # Redis에 캐싱
    set_user_redis(user)

    return user
