from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import create_user
from app.schemas import UserCreate, UserResponse

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, name=user.name, password=user.password, token=user.token)
