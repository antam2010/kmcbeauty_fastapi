import logging

from fastapi import status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.phonebook_crud import (
    create_phonebook,
    get_phonebook_by_id,
    get_phonebooks_by_user,
    update_phonebook,
)
from app.exceptions import CustomException
from app.models.phonebook import Phonebook
from app.models.shop import Shop
from app.models.user import User
from app.schemas.phonebook import (
    PhonebookCreate,
    PhonebookRequest,
    PhonebookResponse,
    PhonebookUpdate,
)

DOMAIN = "PHONEBOOK"


# 전화번호부 목록 조회 서비스
def get_phonebook_list_service(
    db: Session,
    params: PhonebookRequest,
    current_shop: Shop,
) -> Page[PhonebookResponse]:
    list = get_phonebooks_by_user(
        db=db, shop_id=current_shop.id, group_name=params.group_name
    )
    return paginate(list)


# 전화번호부 상세 조회 서비스
def get_phonebook_service(
    db: Session, current_shop: Shop, phonebook_id: int
) -> PhonebookResponse:
    phonebook = get_phonebook_by_id(db, phonebook_id, current_shop.id)
    if not phonebook:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)
    return phonebook


# 전화번호부 생성
def create_phonebook_service(
    db: Session,
    data: PhonebookCreate,
    current_shop: Shop,
) -> PhonebookResponse:

    try:
        phonebook = create_phonebook(db, data, current_shop.id)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logging.exception(f"IntegrityError: {e}")
        raise CustomException(status_code=status.HTTP_409_CONFLICT, domain=DOMAIN)
    except SQLAlchemyError as e:
        db.rollback()
        logging.exception(f"SQLAlchemyError: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )
    except Exception as e:
        db.rollback()
        logging.exception(f"Unexpected error: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )
    db.refresh(phonebook)
    return phonebook


# 전화번호부 수정
def update_phonebook_service(
    db: Session, phonebook_id: int, data: PhonebookUpdate, current_shop: Shop
) -> Phonebook:

    phonebook = get_phonebook_by_id(db, phonebook_id, current_shop.id)
    if not phonebook:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)

    try:
        update_phonebook(db, phonebook, data)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logging.exception(f"IntegrityError: {e}")
        raise CustomException(status_code=status.HTTP_409_CONFLICT, domain=DOMAIN)
    except SQLAlchemyError as e:
        db.rollback()
        logging.exception(f"SQLAlchemyError: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )
    except Exception as e:
        db.rollback()
        logging.exception(f"Unexpected error: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )
    db.refresh(phonebook)
    return phonebook


def delete_phonebook_service(db: Session, phonebook_id: int, current_user: User):
    phonebook = get_phonebook_by_id(db, phonebook_id, current_user.id)
    if not phonebook:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)
    try:
        db.delete(phonebook)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, domain=DOMAIN
        )
    db.delete(phonebook)
    db.commit()
