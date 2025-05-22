from fastapi import status
from sqlalchemy.orm import Session

from app.crud.shop_invite_curd import create_invite, get_valid_invite
from app.crud.shop_user_crud import get_shop_user
from app.exceptions import CustomException
from app.models.user import User
from app.schemas.shop_invite import ShopInviteResponse

DOMAIN = "SHOP_INVITE"


def generate_invite_code_service(
    db: Session,
    shop_id: int,
    user: User,
) -> ShopInviteResponse:
    """초대코드 생성 서비스.

    :param db: DB 세션
    :param shop_id: 샵 ID
    :param user: 유저 정보
    :return: 초대코드 정보
    """
    # 권한 확인: 대표 원장만 생성 가능
    shop_user = get_shop_user(db, shop_id, user.id)
    if not shop_user:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            domain=DOMAIN,
            detail="해당 샵에 소속되지 않았습니다.",
        )
    if not shop_user.is_primary_owner:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            domain=DOMAIN,
            detail="초대코드를 생성할 권한이 없습니다.",
        )

    # 중복 생성 방지
    if get_valid_invite(db, shop_id):
        raise CustomException(
            status_code=status.HTTP_409_CONFLICT,
            domain=DOMAIN,
            detail="이미 활성화된 초대코드가 존재합니다.",
        )

    # 생성
    invite = create_invite(db, shop_id)

    return ShopInviteResponse(
        invite_code=invite.invite_code,
        expired_at=invite.expired_at,
    )
