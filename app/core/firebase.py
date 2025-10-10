import logging
import os
from typing import Any

import firebase_admin
from firebase_admin import credentials, messaging

logger = logging.getLogger(__name__)

# Firebase 서비스 계정 키 파일 경로 (환경변수에서 읽기)
SERVICE_ACCOUNT_KEY_PATH = os.getenv(
    "FIREBASE_SERVICE_ACCOUNT_KEY_PATH",
    "firebase-service-account.json",
)

# Firebase 초기화
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin SDK initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase Admin SDK: {e}")


def send_fcm_message(
    token: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> dict[str, Any]:
    """FCM 메시지를 전송합니다.

    Args:
        token: FCM 디바이스 토큰
        title: 푸시 알림 제목
        body: 푸시 알림 내용
        data: 추가 데이터 (선택사항)

    Returns:
        dict: 메시지 전송 결과

    Raises:
        Exception: 메시지 전송 실패 시

    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )
        response = messaging.send(message)
        logger.info(f"FCM message sent successfully: {response}")
        return {"success": True, "message_id": response}
    except Exception as e:
        logger.error(f"Failed to send FCM message: {e}")
        raise


def send_fcm_multicast(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> dict[str, Any]:
    """여러 디바이스에 FCM 메시지를 전송합니다.

    Args:
        tokens: FCM 디바이스 토큰 리스트
        title: 푸시 알림 제목
        body: 푸시 알림 내용
        data: 추가 데이터 (선택사항)

    Returns:
        dict: 메시지 전송 결과

    Raises:
        Exception: 메시지 전송 실패 시

    """
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
        )
        response = messaging.send_multicast(message)
        logger.info(
            f"FCM multicast sent: {response.success_count} successful, "
            f"{response.failure_count} failed",
        )
        return {
            "success": True,
            "success_count": response.success_count,
            "failure_count": response.failure_count,
        }
    except Exception as e:
        logger.error(f"Failed to send FCM multicast: {e}")
        raise
