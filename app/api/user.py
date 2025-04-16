from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import (create_user_service, get_user_service,
                                       update_user_service)

# 사용자 관련 API 그룹 지
router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="사용자 조회",
    description="현재 로그인한 사용자의 정보를 조회합니다.",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "사용자를 찾을 수 없음"},
    },
)
def read_user_handler(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_service(db, current_user)


@router.post(
    "/",
    response_model=UserResponse,
    summary="사용자 생성",
    description="새로운 사용자를 생성합니다.",
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "중복 에러"},
    },
)
def create_user_handler(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(db, user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="사용자 수정",
    description="사용자 정보를 수정합니다.",
    status_code=200,
    responses={
        404: {"description": "사용자를 찾을 수 없음"},
        409: {"description": "중복 에러"},
    },
)
def update_user_handler(
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user_service(db, user, current_user)
