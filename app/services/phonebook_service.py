from fastapi import HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.phonebook import (create_phonebook, get_phonebook_by_id,
                                get_phonebooks_by_user, update_phonebook)
from app.models.phonebook import Phonebook
from app.models.user import User
from app.schemas.phonebook import (PhonebookCreate, PhonebookListRequest,
                                   PhonebookUpdate)


# 전화번호부 목록 조회 서비스
def get_phonebook_list_service(
    db: Session, current_user: User, params: PhonebookListRequest
) -> Page[Phonebook]:
    list = get_phonebooks_by_user(
        db, user_id=current_user.id, group_name=params.group_name
    )
    return paginate(list)


# 전화번호부 상세 조회 서비스
def get_phonebook_service(
    db: Session, current_user: User, phonebook_id: int
) -> Phonebook:
    phonebook = get_phonebook_by_id(db, phonebook_id, current_user.id)
    if not phonebook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return phonebook


# 전화번호부 생성
def create_phonebook_service(
    db: Session, data: PhonebookCreate, current_user: User
) -> Phonebook:

    new_item = create_phonebook(db, data, current_user.id)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    db.refresh(new_item)

    return new_item


# 전화번호부 수정
def update_phonebook_service(
    db: Session, phonebook_id: int, data: PhonebookUpdate, current_user: User
) -> Phonebook:

    phonebook = get_phonebook_by_id(db, phonebook_id, current_user.id)
    if not phonebook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    update_phonebook(db, phonebook, data)

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    db.refresh(phonebook)
    return phonebook


def delete_phonebook_service(db: Session, phonebook_id: int, current_user: User):
    phonebook = get_phonebook_by_id(db, phonebook_id, current_user.id)
    if not phonebook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        db.delete(phonebook)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    db.delete(phonebook)
    db.commit()
