from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.shop_user_crud import get_shop_users_by_shop_id
from app.exceptions import CustomException
from app.schemas.shop_user import ShopUserUserResponse

DOMAIN = "SHOP_USER"


def get_shop_users_service(db: Session, shop_id: int) -> list[ShopUserUserResponse]:
    """샵 목록 조회 서비스.

    :param db: DB 세션
    :param user: 현재 로그인한 유저
    :return: 샵 목록
    """
    try:
        return get_shop_users_by_shop_id(db=db, shop_id=shop_id)
    except SQLAlchemyError as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            detail="DB Error",
            exception=e,
        ) from e
    except Exception as e:
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        ) from e
