import json

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.redis_client import redis_client
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWTError: {e}")
        raise credentials_exception

    cache_key = f"user:{user_id}"
    cached_user_json = redis_client.get(cache_key)

    if cached_user_json:
        cached_user = json.loads(cached_user_json)
        db_updated_at = (
            db.query(User.updated_at).filter(User.id == int(user_id)).scalar()
        )
        if cached_user["updated_at"] == db_updated_at.isoformat():
            return User(**cached_user)  # 캐시된 정보 그대로 사용

    # 캐시 없거나 outdated → DB 조회
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise credentials_exception

    # Redis에 캐시 저장
    redis_client.setex(
        cache_key,
        60 * 60,
        json.dumps(
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "updated_at": user.updated_at.isoformat(),
            }
        ),
    )

    return user
