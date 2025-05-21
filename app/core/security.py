from datetime import UTC, datetime, timedelta

from cryptography.fernet import Fernet
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from app.core.config import ALGORITHM, FERNET_KEY, SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fernet = Fernet(FERNET_KEY.encode())


class TokenDecodeError(Exception):
    """JWT 디코딩 실패 시 커스텀 예외"""



def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    now = datetime.now(UTC)
    expire = now + expires_delta

    to_encode.update(
        {
            "exp": expire,  # 만료 시각
            "iat": now,  # 발급 시각
            "nbf": now,  # 이 시점부터 유효 (optional)
        },
    )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise TokenDecodeError("Access token has expired.")
    except JWTError:
        raise TokenDecodeError("Invalid access token.")
    except Exception:
        raise TokenDecodeError("Unexpected token decode error.")


def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
