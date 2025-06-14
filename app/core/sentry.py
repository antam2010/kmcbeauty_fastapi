import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def before_send(event, hint):
    import os

    env = os.getenv("APP_ENV", "local")

    if env in ["local", "debug"]:
        return None  # 완전히 차단하고 싶으면 이렇게

    return event


def init_sentry(
    dsn: str,
    environment: str,
    traces_sample_rate: float = 0.2,
    profiles_sample_rate: float = 0.0,
):
    """Sentry SDK 초기화 함수

    Args:
        dsn (str): Sentry DSN URL
        environment (str): 실행 환경 (예: local, debug, production)
        traces_sample_rate (float): 성능 추적 샘플 비율 (0.0 ~ 1.0)
        profiles_sample_rate (float): CPU 프로파일링 샘플 비율 (0.0 ~ 1.0)

    """
    # Sentry에서 로깅도 연동할 수 있도록 설정
    sentry_logging = LoggingIntegration(
        level="INFO",  # breadcrumb 수집 로그 레벨 (INFO 이상 수집)
        event_level="ERROR",  # 이벤트로 전송할 최소 로그 레벨
    )

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            FastApiIntegration(),  # FastAPI 프레임워크 연동
            sentry_logging,  # Logging 연동
        ],
        traces_sample_rate=traces_sample_rate,  # 요청 성능 수집 비율
        profiles_sample_rate=profiles_sample_rate,  # CPU/메모리 프로파일링 비율
        environment=environment,  # 환경 구분(local, debug, prod)
        send_default_pii=True,  # 개인정보 전송 허용
        before_send=before_send,  # 이벤트 전송 전 처리 함수
    )
