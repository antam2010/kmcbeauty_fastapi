import logging

from sqlalchemy.orm import Session

from app.core.limits import USER_DEVICE_TOKENS_MAX
from app.models.device_push_token import DevicePushToken

logger = logging.getLogger(__name__)


def get_device_token_by_id(db: Session, token_id: int) -> DevicePushToken | None:
    """디바이스 푸시 토큰 ID로 조회."""
    return db.query(DevicePushToken).filter(DevicePushToken.id == token_id).first()


def get_device_tokens_by_user(
    db: Session,
    user_id: int,
    is_active: bool = True,
) -> list[DevicePushToken]:
    """유저 ID로 디바이스 푸시 토큰 목록 조회.

    SPEC-PERF-001 REQ-PERF-004: `/device-tokens/me` 언바운드 조회 방어 상한.
    구조적으로 소규모(유저당 디바이스 수)지만 코드상 상한이 없으므로 방어 캡을
    둔다. 응답 shape(list[...])는 유지한다. 상한 도달 시 절단 가능성을 경고
    로그로 남긴다.
    """
    query = db.query(DevicePushToken).filter(DevicePushToken.user_id == user_id)
    if is_active:
        query = query.filter(DevicePushToken.is_active == is_active)
    # 캡(.limit) 전에 결정적 정렬을 보장한다(SPEC-PERF-001 REQ-PERF-004).
    # FCM 전송 경로도 이 함수를 공유하므로 안정적 순서가 운영에서도 의미가 있다.
    tokens = (
        query.order_by(DevicePushToken.id.desc())
        .limit(USER_DEVICE_TOKENS_MAX)
        .all()
    )
    if len(tokens) >= USER_DEVICE_TOKENS_MAX:
        logger.warning(
            "get_device_tokens_by_user hit row cap (%d) for user_id=%s; "
            "result may be truncated",
            USER_DEVICE_TOKENS_MAX,
            user_id,
        )
    return tokens


def get_device_tokens_by_shop(
    db: Session,
    shop_id: int,
    is_active: bool = True,
) -> list[DevicePushToken]:
    """샵 ID로 디바이스 푸시 토큰 목록 조회."""
    query = db.query(DevicePushToken).filter(DevicePushToken.shop_id == shop_id)
    if is_active:
        query = query.filter(DevicePushToken.is_active == is_active)
    return query.all()


def create_device_token(
    db: Session,
    device_token_data: dict,
) -> DevicePushToken:
    """디바이스 푸시 토큰 생성."""
    device_token = DevicePushToken(**device_token_data)
    db.add(device_token)
    db.flush()
    return device_token


def update_device_token(
    db: Session,
    device_token: DevicePushToken,
    update_data: dict,
) -> DevicePushToken:
    """디바이스 푸시 토큰 업데이트."""
    for key, value in update_data.items():
        if value is not None:
            setattr(device_token, key, value)
    db.flush()
    return device_token


def delete_device_token(db: Session, device_token: DevicePushToken) -> None:
    """디바이스 푸시 토큰 삭제."""
    db.delete(device_token)
    db.flush()


def deactivate_device_token(
    db: Session,
    device_token: DevicePushToken,
) -> DevicePushToken:
    """디바이스 푸시 토큰 비활성화."""
    device_token.is_active = False
    db.flush()
    return device_token


def get_or_create_device_token(
    db: Session,
    user_id: int | None,
    shop_id: int | None,
    device_id: str | None,
    token: str,
    platform: str,
) -> DevicePushToken:
    """디바이스 푸시 토큰 조회 또는 생성 (토큰 기준)."""
    # 기존 토큰 조회
    existing = db.query(DevicePushToken).filter(DevicePushToken.token == token).first()

    if existing:
        # 기존 토큰 업데이트
        existing.user_id = user_id
        existing.shop_id = shop_id
        existing.device_id = device_id
        existing.platform = platform
        existing.is_active = True
        db.flush()
        return existing

    # 새 토큰 생성
    new_token = DevicePushToken(
        user_id=user_id,
        shop_id=shop_id,
        device_id=device_id,
        token=token,
        platform=platform,
        is_active=True,
    )
    db.add(new_token)
    db.flush()
    return new_token
