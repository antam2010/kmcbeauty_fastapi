from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.model.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user: UserCreate) -> User:
    """
    사용자 생성: 비밀번호 해시 후 저장
    """
    user_data = user.model_dump()
    user_data["password"] = hash_password(user.password)

    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    user_id 기준 사용자 단순 조회 (권한 체크 없음)
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user_db(db: Session, db_user: User, user_data: dict) -> User:
    """
    이미 조회된 User 객체에 대해 업데이트 수행
    """
    for key, value in user_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user
