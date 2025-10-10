from fastapi import status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.firebase import send_fcm_message, send_fcm_multicast
from app.crud.device_push_token_crud import (
    delete_device_token,
    get_device_token_by_id,
    get_device_tokens_by_shop,
    get_device_tokens_by_user,
    get_or_create_device_token,
    update_device_token,
)
from app.exceptions import CustomException
from app.models.user import User
from app.schemas.device_push_token import (
    DevicePushTokenCreate,
    DevicePushTokenResponse,
    DevicePushTokenUpdate,
    FCMMessageRequest,
    FCMMessageResponse,
)

DOMAIN = "DEVICE_PUSH_TOKEN"


def register_device_token_service(
    db: Session,
    token_data: DevicePushTokenCreate,
    current_user: User,
) -> DevicePushTokenResponse:
    """디바이스 푸시 토큰 등록 (생성 또는 업데이트)."""
    try:
        # 기존 토큰이 있으면 업데이트, 없으면 생성
        device_token = get_or_create_device_token(
            db=db,
            user_id=token_data.user_id or current_user.id,
            shop_id=token_data.shop_id,
            device_id=token_data.device_id,
            token=token_data.token,
            platform=token_data.platform,
        )
        db.commit()
        db.refresh(device_token)
        return DevicePushTokenResponse.model_validate(device_token)
    except IntegrityError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_409_CONFLICT,
            domain=DOMAIN,
            detail="Token already exists",
            exception=e,
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e


def get_my_device_tokens_service(
    db: Session,
    current_user: User,
) -> list[DevicePushTokenResponse]:
    """내 디바이스 푸시 토큰 목록 조회."""
    try:
        tokens = get_device_tokens_by_user(
            db=db,
            user_id=current_user.id,
            is_active=True,
        )
        return [DevicePushTokenResponse.model_validate(t) for t in tokens]
    except SQLAlchemyError as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e


def update_device_token_service(
    db: Session,
    token_id: int,
    token_update: DevicePushTokenUpdate,
    current_user: User,
) -> DevicePushTokenResponse:
    """디바이스 푸시 토큰 업데이트."""
    try:
        device_token = get_device_token_by_id(db, token_id)
        if not device_token:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                domain=DOMAIN,
                detail="Device token not found",
            )

        # 권한 확인
        if device_token.user_id != current_user.id:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                domain=DOMAIN,
                detail="Access denied",
            )

        update_data = token_update.model_dump(exclude_unset=True)
        updated_token = update_device_token(db, device_token, update_data)
        db.commit()
        db.refresh(updated_token)
        return DevicePushTokenResponse.model_validate(updated_token)
    except CustomException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e


def delete_device_token_service(
    db: Session,
    token_id: int,
    current_user: User,
) -> None:
    """디바이스 푸시 토큰 삭제."""
    try:
        device_token = get_device_token_by_id(db, token_id)
        if not device_token:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                domain=DOMAIN,
                detail="Device token not found",
            )

        # 권한 확인
        if device_token.user_id != current_user.id:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                domain=DOMAIN,
                detail="Access denied",
            )

        delete_device_token(db, device_token)
        db.commit()
    except CustomException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e


def send_fcm_notification_service(
    db: Session,
    fcm_request: FCMMessageRequest,
    current_user: User,
) -> FCMMessageResponse:
    """FCM 푸시 알림 전송."""
    try:
        # user_id 또는 shop_id 중 하나는 필수
        if not fcm_request.user_id and not fcm_request.shop_id:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST,
                domain=DOMAIN,
                detail="Either user_id or shop_id is required",
            )

        # 디바이스 토큰 조회
        if fcm_request.user_id:
            tokens = get_device_tokens_by_user(
                db=db,
                user_id=fcm_request.user_id,
                is_active=True,
            )
        else:
            tokens = get_device_tokens_by_shop(
                db=db,
                shop_id=fcm_request.shop_id,
                is_active=True,
            )

        if not tokens:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                domain=DOMAIN,
                detail="No active device tokens found",
            )

        # FCM 메시지 전송
        token_strings = [t.token for t in tokens]

        if len(token_strings) == 1:
            # 단일 디바이스
            result = send_fcm_message(
                token=token_strings[0],
                title=fcm_request.title,
                body=fcm_request.body,
                data=fcm_request.data,
            )
            return FCMMessageResponse(
                success=result["success"],
                message_id=result["message_id"],
            )
        # 여러 디바이스
        result = send_fcm_multicast(
            tokens=token_strings,
            title=fcm_request.title,
            body=fcm_request.body,
            data=fcm_request.data,
        )
        return FCMMessageResponse(
            success=result["success"],
            success_count=result["success_count"],
            failure_count=result["failure_count"],
        )

    except CustomException:
        raise
    except Exception as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            detail=f"Failed to send FCM notification: {e!s}",
            exception=e,
        ) from e
