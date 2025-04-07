import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# 1. .env 파일 로드
base_dir = Path(__file__).resolve().parent.parent

# 기본 ENV 선택 (dev or prod)
load_dotenv(dotenv_path=base_dir / ".env")
env = os.getenv("ENV", "dev")
env_path = base_dir / f".env.{env}"

# 환경별 .env 로드 (.env.dev 또는 .env.prod)
load_dotenv(dotenv_path=env_path, override=True)

# 2. DB 연결 정보 설정
from app.database import DATABASE_URL

# 모델 import: 자동 생성에 필요함
from app.model import phonebook, user
from app.model.base import Base

# Alembic 설정 객체
config = context.config

# sqlalchemy.url 설정
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 로그 설정
if config.config_file_name:
    fileConfig(config.config_file_name)

# metadata 등록
target_metadata = Base.metadata


# 오프라인 모드
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# 온라인 모드
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


# 실행
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
