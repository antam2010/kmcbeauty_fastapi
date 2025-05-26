from sqlalchemy.orm import Session

from app.models.user import User


def create_user(db: Session, user_data: dict) -> User:
    """사용자 생성."""
    new_user = User(**user_data)
    db.add(new_user)
    db.flush()
    return new_user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """user_id 기준 사용자 단순 조회 (권한 체크 없음)."""
    return db.query(User).filter(User.id == user_id).first()


def update_user_db(db: Session, user: User, user_data: dict) -> User:
    for key, value in user_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """이메일 기준 사용자 단순 조회 (권한 체크 없음)."""
    return db.query(User).filter(User.email == email).first()
