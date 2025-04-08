from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import (
    create_user_service,
    get_user_if_authorized,
    update_user_if_authorized,
)

# 사용자 관련 API 그룹 지
router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 조회",
    description="사용자 정보를 조회합니다.",
)
def read_user_handler(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_if_authorized(db, user_id, current_user)


@router.post(
    "/",
    response_model=UserResponse,
    summary="사용자 생성",
    description="새로운 사용자를 생성합니다.",
    status_code=201,
)
def create_user_handler(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_user_service(db, user, current_user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="사용자 수정",
    description="사용자 정보를 수정합니다.",
)
def update_user_handler(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user_if_authorized(db, user_id, user, current_user)
