from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sentry_sdk import set_user
from sqlalchemy.orm import Session

from app.core.security import TokenDecodeError, decode_jwt_token
from app.database import get_db
from app.exceptions import CustomException
from app.models.user import User
from app.utils.redis.user import clear_user_redis, get_user_redis, set_user_redis

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
DOMAIN = "AUTH"


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_jwt_token(token)
        user_id = payload.get("sub")
        if not user_id:
            error_msg = "sub(claim) not found in token"
            raise ValueError(error_msg)

        user_id = int(user_id)

    except (TokenDecodeError, ValueError) as e:
        raise CustomException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            domain=DOMAIN,
            hint="유효하지 않은 인증 토큰입니다.",
            exception=e,
        ) from e
    except Exception as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            hint="인증 토큰 처리 중 오류가 발생했습니다.",
            exception=e,
        ) from e

    # Redis → fallback to DB
    if user_redis := get_user_redis(user_id):
        user = User(**user_redis)
    else:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise CustomException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                domain=DOMAIN,
                hint="사용자를 찾을 수 없습니다.",
            )
        set_user_redis(user)  # ORM 객체를 캐싱

    # Sentry 사용자 식별 정보 설정
    set_user({"id": user.id, "email": user.email})
    return user


def clear_current_user_cache(
    user_id: int,
) -> None:
    """현재 사용자 캐시를 제거합니다.

    주로 로그아웃 시 사용됩니다.
    """
    clear_user_redis(user_id)
