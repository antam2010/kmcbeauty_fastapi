from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.shop import get_current_shop
from app.docs.common_responses import COMMON_ERROR_RESPONSES
from app.models.user import User
from app.schemas.phonebook import (
    PhonebookCreate,
    PhonebookFilter,
    PhonebookResponse,
    PhonebookUpdate,
)
from app.services.phonebook_service import (
    create_phonebook_service,
    delete_phonebook_service,
    get_phonebook_list_service,
    get_phonebook_service,
    update_phonebook_service,
)

router = APIRouter(prefix="/phonebooks", tags=["Phonebook"])


# 전화번호부 목록 조회
@router.get(
    "/",
    response_model=Page[PhonebookResponse],
    summary="전화번호부 목록 조회",
    description="전화번호부 목록을 조회합니다.",
    status_code=status.HTTP_200_OK,
)
def list_phonebook(
    params: PhonebookFilter = Depends(),
    db: Session = Depends(get_db),
    current_shop: User = Depends(get_current_shop),
) -> Page[PhonebookResponse]:
    return get_phonebook_list_service(
        db,
        params=params,
        current_shop=current_shop,
    )


# 전화번호부 상세 조회
@router.get(
    "/{phonebook_id}",
    response_model=PhonebookResponse,
    summary="전화번호부 상세 조회",
    description="전화번호부 항목을 상세 조회합니다.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: COMMON_ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
    },
)
def read_phonebook_handler(
    phonebook_id: int,
    db: Session = Depends(get_db),
    current_shop: User = Depends(get_current_shop),
) -> PhonebookResponse:
    return get_phonebook_service(db, current_shop, phonebook_id)


# 전화번호부 생성
@router.post(
    "/",
    response_model=PhonebookResponse,
    summary="전화번호부 생성",
    description="새로운 전화번호부 항목을 생성합니다.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: COMMON_ERROR_RESPONSES[status.HTTP_409_CONFLICT],
    },
)
def create_phonebook_handler(
    phonebook: PhonebookCreate,
    db: Session = Depends(get_db),
    current_shop: User = Depends(get_current_shop),
) -> PhonebookResponse:
    return create_phonebook_service(db, phonebook, current_shop)


# 전화번호부 수정
@router.put(
    "/{phonebook_id}",
    response_model=PhonebookResponse,
    summary="전화번호부 수정",
    description="전화번호부 항목을 수정합니다.",
    status_code=status.HTTP_200_OK,
)
def update_phonebook_handler(
    phonebook_id: int,
    phonebook: PhonebookUpdate,
    db: Session = Depends(get_db),
    current_shop: User = Depends(get_current_shop),
) -> PhonebookResponse:
    return update_phonebook_service(db, phonebook_id, phonebook, current_shop)


# 전화번호부 삭제
@router.delete(
    "/{phonebook_id}",
    status_code=204,
    summary="전화번호부 삭제",
    description="전화번호부 항목을 소프트 삭제합니다.",
)
def delete_phonebook_handler(
    phonebook_id: int,
    db: Session = Depends(get_db),
    current_shop: User = Depends(get_current_shop),
):
    delete_phonebook_service(db, phonebook_id, current_shop)
    return
