from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.models.phonebook import Phonebook
from app.schemas.phonebook import PhonebookCreate, PhonebookFilter, PhonebookUpdate


# 전화번호부 리스트 조회
def get_phonebooks_by_user(
    db: Session, shop_id: int, group_name: str | None = None
) -> Page[Phonebook]:
    query = db.query(Phonebook).filter(
        Phonebook.shop_id == shop_id,
        Phonebook.deleted_at.is_(None),
    )

    if group_name:
        query = query.filter(Phonebook.group_name.like(f"%{group_name}%"))

    query.order_by(Phonebook.id.desc())

    return paginate(query)


# 전화번호부 상세 조회
def get_phonebook_by_id(
    db: Session, phonebook_id: int, shop_id: int
) -> Phonebook | None:
    phonebook = (
        db.query(Phonebook)
        .filter(
            Phonebook.id == phonebook_id,
            Phonebook.shop_id == shop_id,
            Phonebook.deleted_at.is_(None),
        )
        .first()
    )
    return phonebook


# 전화번호부 생성
def create_phonebook(db: Session, data: PhonebookCreate, shop_id: int) -> Phonebook:
    item = Phonebook(**data.model_dump(), shop_id=shop_id)
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

# 전화번호부 중복 체크
def get_phonebook_by_phone_number(
    db: Session, phone_number: str, shop_id: int
) -> Phonebook | None:
    phonebook = (
        db.query(Phonebook)
        .filter(
            Phonebook.phone_number == phone_number,
            Phonebook.shop_id == shop_id,
            Phonebook.deleted_at.is_(None),
        )
        .first()
    )
    return phonebook