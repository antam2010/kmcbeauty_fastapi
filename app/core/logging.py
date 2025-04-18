# app/core/logging.py

import logging
import sqlparse
import os


def setup_logging(app_env: str = "local"):
    """
    로깅 설정 함수

    Args:
        app_env (str): 실행 환경 (local, debug, production)
    """

    # 기본 로그 레벨 및 파일명 설정
    log_level = logging.INFO
    log_file = "logs/app.log"

    if app_env == "debug":
        log_level = logging.DEBUG
        log_file = "logs/debug.log"
    elif app_env == "production":
        log_level = logging.ERROR
        log_file = "logs/prod.log"
    elif app_env == "local":
        log_level = logging.DEBUG
        log_file = "logs/local.log"

    # 로그 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 로깅 기본 설정: 파일 + 콘솔 출력
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    # SQLAlchemy용 로그 포매터 핸들러 정의
    class SQLFormatterHandler(logging.StreamHandler):
        def emit(self, record):
            if isinstance(record.msg, str):
                try:
                    record.msg = sqlparse.format(
                        record.msg,
                        reindent=True,
                        keyword_case="upper",
                    )
                except Exception:
                    pass
            super().emit(record)

    # SQLAlchemy 엔진 로그 설정
    sql_logger = logging.getLogger("sqlalchemy.engine")
    sql_logger.setLevel(logging.INFO)
    sql_logger.handlers.clear()

    sql_handler = SQLFormatterHandler()
    sql_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
    sql_logger.addHandler(sql_handler)
