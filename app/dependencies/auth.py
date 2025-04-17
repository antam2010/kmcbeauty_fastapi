import logging

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET_KEY
from app.database import get_db
from app.exceptions import CustomException
from app.models.user import User
from app.utils.redis.user import get_user_redis, set_user_redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
credentials_exception = CustomException(
    status_code=status.HTTP_401_UNAUTHORIZED, domain="AUTH"
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        logging.exception("JWTError: %s", e)
        raise credentials_exception

    user_id = int(user_id)

    # Redis에서 사용자 캐시 조회
    cached_user = get_user_redis(user_id)
    if cached_user:
        return User(**cached_user)

    # Redis에 없으면 DB에서 조회
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logging.exception("User not found: %s", user_id)
        raise credentials_exception

    # Redis에 캐싱
    set_user_redis(user)

    return user
