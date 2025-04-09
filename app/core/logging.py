import logging

import sqlparse


def setup_logging(app_env: str = "local"):
    # 기본 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler(),
        ],
    )

    # 환경별 로그 레벨 설정
    if app_env == "local":
        logging.getLogger().setLevel(logging.INFO)
    elif app_env == "debug":
        logging.getLogger().setLevel(logging.DEBUG)
    elif app_env == "production":
        logging.getLogger().setLevel(logging.ERROR)

    # SQLAlchemy 쿼리 포매터 설정
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

    sql_logger = logging.getLogger("sqlalchemy.engine")
    sql_logger.setLevel(logging.INFO)
    sql_logger.handlers.clear()

    sql_handler = SQLFormatterHandler()
    sql_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
    sql_logger.addHandler(sql_handler)
