import logging
from collections import defaultdict

from fastapi import status
from fastapi_pagination import Page
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.phonebook_crud import (
    create_phonebook,
    get_all_phonebooks_by_shop,
    get_group_counts_by_groupname,
    get_phonebook_by_id,
    get_phonebook_by_phone_number,
    get_phonebooks_by_user,
    update_phonebook,
)
from app.exceptions import CustomException
from app.models.phonebook import Phonebook
from app.models.shop import Shop
from app.schemas.phonebook import (
    PhonebookCreate,
    PhonebookFilter,
    PhonebookGroupedByGroupnameResponse,
    PhonebookResponse,
    PhonebookUpdate,
)

DOMAIN = "PHONEBOOK"


# 전화번호부 목록 조회 서비스
def get_phonebook_list_service(
    db: Session,
    params: PhonebookFilter,
    current_shop: Shop,
) -> Page[PhonebookResponse]:
    list = get_phonebooks_by_user(db=db, shop_id=current_shop.id, search=params.search)
    return list


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
        # 전화번호부 중복 체크
        existing = get_phonebook_by_phone_number(db, data.phone_number, current_shop.id)
        if existing:
            raise CustomException(
                status_code=status.HTTP_409_CONFLICT,
                domain=DOMAIN,
                hint="전화번호 중복 확인하쇼.",
            )
        phonebook = create_phonebook(db, data, current_shop.id)
        db.commit()
    except CustomException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        )
    except Exception as e:
        db.rollback()
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
            exception=e,
        )
    db.refresh(phonebook)
    return phonebook


# 전화번호부 수정
def update_phonebook_service(
    db: Session, phonebook_id: int, data: PhonebookUpdate, current_shop: Shop
) -> Phonebook:

    existing = get_phonebook_by_phone_number(db, data.phone_number, current_shop.id)
    if existing and existing.id != phonebook_id:
        raise CustomException(status_code=status.HTTP_409_CONFLICT, domain=DOMAIN)

    phonebook = get_phonebook_by_id(db, phonebook_id, current_shop.id)
    if not phonebook:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND, domain=DOMAIN)

    try:
        update_phonebook(db, phonebook, data)
        db.commit()
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


def delete_phonebook_service(db: Session, phonebook_id: int, current_shop: Shop):
    phonebook = get_phonebook_by_id(db, phonebook_id, current_shop.id)
    if not phonebook:
        raise CustomException(
            status_code=status.HTTP_404_NOT_FOUND,
            domain=DOMAIN,
        )
    try:
        Phonebook.soft_delete(phonebook)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logging.exception(f"SQLAlchemyError occurred while deleting phonebook: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
        )
    except Exception as e:
        db.rollback()
        logging.exception(f"Unexpected error occurred while deleting phonebook: {e}")
        raise CustomException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            domain=DOMAIN,
        )


def get_grouped_by_groupname_service(
    db: Session, current_shop: Shop, with_items: bool
) -> list[PhonebookGroupedByGroupnameResponse]:

    # 그룹별 count만 조회
    group_data = get_group_counts_by_groupname(db, current_shop.id)

    group_map: dict[str | None, list[PhonebookResponse]] = defaultdict(list)

    if with_items:
        # 한 번에 전체 phonebook 가져옴 (deleted 제외)
        all_items = get_all_phonebooks_by_shop(db, current_shop.id)

        for item in all_items:
            key = item.group_name
            group_map[key].append(PhonebookResponse.model_validate(item))

    result = []
    for group_name, count in group_data:
        items = group_map[group_name] if with_items else []

        result.append(
            PhonebookGroupedByGroupnameResponse(
                group_name=group_name,
                count=count,
                items=items,
            )
        )

    return result
