from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import create_user
from app.schemas import UserCreate, UserResponse

# 사용자 관련 API 그룹 지
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=UserResponse, summary="사용자 생성", description="새로운 사용자를 생성합니다.")
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)
