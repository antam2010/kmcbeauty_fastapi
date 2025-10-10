from sqlalchemy.orm import Session

from app.models.device_push_token import DevicePushToken


def get_device_token_by_id(db: Session, token_id: int) -> DevicePushToken | None:
    """디바이스 푸시 토큰 ID로 조회."""
    return db.query(DevicePushToken).filter(DevicePushToken.id == token_id).first()


def get_device_tokens_by_user(
    db: Session,
    user_id: int,
    is_active: bool = True,
) -> list[DevicePushToken]:
    """유저 ID로 디바이스 푸시 토큰 목록 조회."""
    query = db.query(DevicePushToken).filter(DevicePushToken.user_id == user_id)
    if is_active:
        query = query.filter(DevicePushToken.is_active == is_active)
    return query.all()


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
