import logging
import os

import sqlparse


def setup_logging(app_env: str):
    """
    로깅 설정 함수

    Args:
        app_env (str): 실행 환경 (local, debug, production)
    """

    # 1) 기본 로깅 레벨 및 파일명 설정
    log_level = logging.INFO
    log_file = "logs/app.log"
    sql_log_level = logging.INFO

    if app_env == "debug":
        log_level = logging.DEBUG
        log_file = "logs/debug.log"
        sql_log_level = logging.ERROR
    elif app_env == "stage":
        log_level = logging.INFO
        log_file = "logs/stage.log"
        sql_log_level = logging.ERROR
    elif app_env == "production":
        log_level = logging.INFO
        log_file = "logs/prod.log"
        sql_log_level = logging.ERROR
    elif app_env == "local":
        log_level = logging.DEBUG
        log_file = "logs/local.log"
        sql_log_level = logging.DEBUG

    # 2) 로그 디렉토리 생성
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 3) 기본 로깅 설정 (파일 + 콘솔)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    # 4) SQLFormatterHandler 정의 (SQL 문장 예쁘게 출력)
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

    # 5) SQLAlchemy 엔진 로그 설정
    sql_logger = logging.getLogger("sqlalchemy.engine")
    # production 환경이면 ERROR 이상만, 아니면 위에서 지정한 대로
    sql_logger.setLevel(sql_log_level)
    sql_logger.handlers.clear()

    sql_handler = SQLFormatterHandler()
    sql_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))

    # (선택) 핸들러 레벨을 추가로 걸고 싶다면
    sql_handler.setLevel(sql_log_level)

    sql_logger.addHandler(sql_handler)
