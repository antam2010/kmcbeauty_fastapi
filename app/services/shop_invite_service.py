from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.shop_invite_curd import (
    create_invite,
    delete_invite_by_shop_id,
    get_invite_by_shop_id,
    get_valid_invite_by_shop_id,
)
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
        )
    if not shop_user.is_primary_owner:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            domain=DOMAIN,
        )

    try:
        existing = get_valid_invite_by_shop_id(db, shop_id)
        if existing:
            raise CustomException(
                status_code=status.HTTP_409_CONFLICT,
                domain=DOMAIN,
            )

        # 생성
        new_invite = create_invite(db, shop_id)
        db.commit()
        db.refresh(new_invite)

    except CustomException as e:
        db.rollback()
        raise e from e
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e
    except Exception as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e
    return ShopInviteResponse.model_validate(new_invite)


def get_invite_code_service(
    db: Session,
    shop_id: int,
    user: User,
) -> ShopInviteResponse:
    """초대코드 조회 서비스.

    :param db: DB 세션
    :param shop_id: 샵 ID
    :param user: 유저 정보
    :return: 초대코드 정보
    """
    # 권한 확인: 대표 원장만 조회 가능
    shop_user = get_shop_user(db, shop_id, user.id)
    if not shop_user:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            domain=DOMAIN,
        )
    if not shop_user.is_primary_owner:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            domain=DOMAIN,
        )

    try:
        invite = get_invite_by_shop_id(db, shop_id)
        if not invite:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                domain=DOMAIN,
            )
    except CustomException as e:
        raise e from e
    except SQLAlchemyError as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e
    except Exception as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e

    return ShopInviteResponse.model_validate(invite)


def delete_invite_code_service(
    db: Session,
    shop_id: int,
    user: User,
) -> None:
    """초대코드 삭제 서비스.

    :param db: DB 세션
    :param shop_id: 샵 ID
    :param user: 유저 정보
    """
    # 권한 확인: 대표 원장만 삭제 가능
    shop_user = get_shop_user(db, shop_id, user.id)
    if not shop_user:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            domain=DOMAIN,
        )
    if not shop_user.is_primary_owner:
        raise CustomException(
            status_code=status.HTTP_403_FORBIDDEN,
            domain=DOMAIN,
        )

    try:
        invite = get_invite_by_shop_id(db, shop_id)
        if not invite:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                domain=DOMAIN,
            )

        delete_invite_by_shop_id(db, shop_id)
        db.commit()
    except CustomException as e:
        db.rollback()
        raise e from e
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e
    except Exception as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e
