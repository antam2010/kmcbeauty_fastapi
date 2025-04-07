from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.model.user import User
from app.schemas.user import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    # Pydantic 객체를 dict로 변환하고 password만 해시 처리
    user_data = user.model_dump()
    user_data["password"] = hash_password(user.password)

    db_user = User(**user_data)  # model에 직접 매핑
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def select_user(db: Session, user_email: str):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def authenticate_user(db: Session, user_email: str, password: str, token: str | None):
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )
    if token:
        user.token = token
        db.commit()
        db.refresh(user)
    return user
