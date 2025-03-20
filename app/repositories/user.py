from sqlalchemy.orm import Session
from app.model.user import User
from app.schemas import UserCreate
from app.utils import hash_password

def create_user(db: Session, user: UserCreate):
    user_passwd = hash_password(user.password) # 비밀번호 암호화
    db_user = User(name=user.name, password=user_passwd, token=user.token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def select_user(db: Session, user_email: str):
    result = db.query(User).filter(User.email == user_email).first()
    return result