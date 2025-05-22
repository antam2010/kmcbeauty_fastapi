from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.shop_invite_curd import create_invite, get_invite_by_shop_id
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

    try:
        existing = get_invite_by_shop_id(db, shop_id)
        if existing:
            raise CustomException(
                status_code=status.HTTP_409_CONFLICT,
                domain=DOMAIN,
            )

        # 생성
        new_invite = create_invite(db, shop_id)

    except SQLAlchemyError as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e

    return ShopInviteResponse(
        invite_code=new_invite.invite_code,
        expired_at=new_invite.expired_at,
    )
