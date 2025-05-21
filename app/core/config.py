import os

from dotenv import load_dotenv

load_dotenv()

# 기본 환경 설정
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS"))
REFRESH_TOKEN_EXPIRE_SECONDS = int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS"))
APP_ENV = os.getenv("APP_ENV", "local")
SENTRY_DSN = os.getenv("SENTRY_DSN")
FERNET_KEY = os.getenv("FERNET_KEY")
