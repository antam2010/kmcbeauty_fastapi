from sqlalchemy.orm import Session
from app.model.user import User
from app.schemas import UserCreate

def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name, password=user.password, token=user.token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
