from sqlalchemy.orm import Session

from app.models.phonebook import Phonebook
from app.schemas.phonebook import (PhonebookCreate, PhonebookListRequest,
                                   PhonebookUpdate)


# 전화번호부 리스트 조회
def get_phonebooks_by_user(
    db: Session, user_id: int, group_name: str | None = None
) -> list[Phonebook]:
    query = db.query(Phonebook).filter(Phonebook.user_id == user_id)

    if group_name:
        query = query.filter(Phonebook.group_name == group_name)

    return query.order_by(Phonebook.id.desc())


# 전화번호부 상세 조회
def get_phonebook_by_id(
    db: Session, phonebook_id: int, user_id: int
) -> Phonebook | None:
    phonebook = (
        db.query(Phonebook)
        .filter(Phonebook.id == phonebook_id, Phonebook.user_id == user_id)
        .first()
    )
    return phonebook


# 전화번호부 생성
def create_phonebook(db: Session, data: PhonebookCreate, user_id: int) -> Phonebook:
    item = Phonebook(**data.model_dump(), user_id=user_id)
    db.add(item)
    return item


# 전화번호부 수정
def update_phonebook(
    db: Session, phonebook: Phonebook, data: PhonebookUpdate
) -> Phonebook:
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(phonebook, key, value)
    return phonebook
