from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.model.phonebook import Phonebook
from app.model.user import User
from app.schemas.phonebook import PhonebookCreate, PhonebookUpdate

import logging

def get_phonebook_if_authorized(db: Session, phonebook_id: int, current_user: User) -> Phonebook:
    phonebook = db.query(Phonebook).filter(Phonebook.id == phonebook_id).first()
    if not phonebook:
        raise HTTPException(status_code=404)
    if phonebook.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403)
    return phonebook

# 이 함수는 새로운 전화번호부 항목을 생성하는 데 사용됩니다.
def create_phonebook_service(db: Session, data: PhonebookCreate, current_user: User) -> Phonebook:
    
    new_item = Phonebook(**data.model_dump(), user_id=current_user.id)
    db.add(new_item)
    
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        logging.warning(f"IntegrityError: {e}")
        raise HTTPException(status_code=409)
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"SQLAlchemyError: {e}")
        raise HTTPException(status_code=500)
    
    db.refresh(new_item)

    return new_item


def update_phonebook_if_authorized(db: Session, phonebook_id: int, data: PhonebookUpdate, current_user: User) -> Phonebook:
    phonebook = get_phonebook_if_authorized(db, phonebook_id, current_user)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(phonebook, key, value)
    db.commit()
    db.refresh(phonebook)
    return phonebook


def delete_phonebook_if_authorized(db: Session, phonebook_id: int, current_user: User):
    phonebook = get_phonebook_if_authorized(db, phonebook_id, current_user)
    db.delete(phonebook)
    db.commit()

def get_phonebook_list(db: Session, current_user: User, group_name: str | None = None, page: int = 0, page_size: int = 10) -> list[Phonebook]:
    return (
        db.query(Phonebook)
        .filter(Phonebook.user_id == current_user.id)
        .filter(Phonebook.group_name == group_name if group_name else True)
        .order_by(Phonebook.id.desc())
        .offset(page)
        .limit(page_size)
        .all()
    )
