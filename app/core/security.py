from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from app.core.config import ALGORITHM, FERNET_KEY, SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fernet = Fernet(FERNET_KEY.encode())


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    to_encode.update(
        {
            "exp": expire,  # 만료 시각
            "iat": now,  # 발급 시각
            "nbf": now,  # 이 시점부터 유효 (optional)
        }
    )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError as e:
        return e
    except JWTError as e:
        return e
    except Exception as e:
        return e


def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
