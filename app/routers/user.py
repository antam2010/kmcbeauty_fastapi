from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.user import create_user, select_user
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse

# 사용자 관련 API 그룹 지
router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/",
    response_model=UserResponse,
    summary="사용자 생성",
    description="새로운 사용자를 생성합니다.",
    status_code=201,
)
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.get(
    "/{user_email}",
    response_model=UserResponse,
    summary="사용자 조회",
    description="사용자 정보를 조회합니다.",
)
def get_user(user_email: str, db: Session = Depends(get_db)):
    return select_user(db, user_email)


@router.put(
    "/{user_email}",
    response_model=UserResponse,
    summary="사용자 수정",
    description="사용자 정보를 수정합니다.",
)
def update_user(user_email: str, user: UserCreate, db: Session = Depends(get_db)):
    return update_user(db, user_email, user)
