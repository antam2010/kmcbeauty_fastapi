from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.phonebook import (
    PhonebookCreate,
    PhonebookListRequest,
    PhonebookResponse,
    PhonebookUpdate,
)
from app.services.phonebook_service import (
    create_phonebook_service,
    delete_phonebook_service,
    get_phonebook_service,
    get_phonebook_list_service,
    update_phonebook_service,
)

router = APIRouter(prefix="/phonebook", tags=["전화번호부"])


# 전화번호부 목록 조회
@router.get(
    "/",
    response_model=Page[PhonebookResponse],
    summary="전화번호부 목록 조회",
    description="전화번호부 목록을 조회합니다.",
)
def list_phonebook(
    params: PhonebookListRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[PhonebookResponse]:
    return get_phonebook_list_service(
        db,
        current_user=current_user,
        params=params,
    )


# 전화번호부 상세 조회
@router.get(
    "/{phonebook_id}",
    response_model=PhonebookResponse,
    summary="전화번호부 상세 조회",
    description="전화번호부 항목을 상세 조회합니다.",
)
def read_phonebook_handler(
    phonebook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_phonebook_service(db, current_user, phonebook_id)


# 전화번호부 생성
@router.post(
    "/",
    response_model=PhonebookResponse,
    summary="전화번호부 생성",
    description="새로운 전화번호부 항목을 생성합니다.",
    status_code=201,
)
def create_phonebook_handler(
    phonebook: PhonebookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_phonebook_service(db, phonebook, current_user)


# 전화번호부 수정
@router.put(
    "/{phonebook_id}",
    response_model=PhonebookResponse,
    summary="전화번호부 수정",
    description="전화번호부 항목을 수정합니다.",
)
def update_phonebook_handler(
    phonebook_id: int,
    phonebook: PhonebookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_phonebook_service(db, phonebook_id, phonebook, current_user)


# 전화번호부 삭제
@router.delete(
    "/{phonebook_id}",
    status_code=204,
    summary="전화번호부 삭제",
    description="전화번호부 항목을 삭제합니다.",
)
def delete_phonebook_handler(
    phonebook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_phonebook_service(db, phonebook_id, current_user)
    return
