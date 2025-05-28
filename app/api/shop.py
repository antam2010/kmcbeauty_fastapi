from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.docs.common_responses import COMMON_ERROR_RESPONSES
from app.models.shop import Shop
from app.models.user import User
from app.schemas.shop import ShopCreate, ShopResponse, ShopSelect, ShopUpdate
from app.schemas.shop_invite import ShopInviteResponse
from app.schemas.shop_user import ShopUserUserResponse
from app.services.shop_invite_service import (
    delete_invite_code_service,
    generate_invite_code_service,
    get_invite_code_service,
)
from app.services.shop_service import (
    delete_selected_shop_service,
    get_my_shops_service,
    get_selected_shop_service,
    set_selected_shop_service,
    upsert_shop_service,
)
from app.services.shop_user_service import get_shop_users_service

router = APIRouter(prefix="/shops", tags=["상점"])


@router.get(
    "",
    response_model=Page[ShopResponse],
    summary="내 샵 목록 조회",
    description="로그인한 유저의 샵 목록을 조회합니다.",
    status_code=status.HTTP_200_OK,
)
def get_my_shops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[ShopResponse]:
    return get_my_shops_service(db=db, user=current_user)


@router.post(
    "",
    response_model=ShopResponse,
    summary="샵 생성",
    description="새로운 샵을 생성합니다.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: COMMON_ERROR_RESPONSES[status.HTTP_403_FORBIDDEN],
    },
)
def create_shop(
    shop_data: ShopCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShopResponse:
    return upsert_shop_service(db=db, user=current_user, shop_data=shop_data)


@router.put(
    "/{shop_id}",
    response_model=ShopResponse,
    summary="샵 수정",
    description="샵 정보를 수정합니다.",
    status_code=status.HTTP_200_OK,
)
def update_shop(
    shop_id: int,
    shop_data: ShopUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShopResponse:
    return upsert_shop_service(
        db=db,
        user=current_user,
        shop_data=shop_data,
        shop_id=shop_id,
    )


@router.post(
    "/selected",
    summary="선택한 샵 설정",
    description="현재 선택한 샵을 설정합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: COMMON_ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
    },
)
def select_shop(
    params: ShopSelect,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    return set_selected_shop_service(db=db, user=current_user, shop_id=params.shop_id)


@router.get(
    "/selected",
    response_model=ShopResponse,
    summary="선택한 샵 조회",
    description="현재 선택된 샵을 조회합니다.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: COMMON_ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
    },
)
def get_selected_shop(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Shop:
    return get_selected_shop_service(db=db, user=current_user)


@router.delete(
    "/selected",
    summary="선택한 샵 삭제",
    description="현재 선택된 샵을 삭제합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: COMMON_ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
    },
)
def delete_selected_shop(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    return delete_selected_shop_service(user=current_user)


@router.post(
    "/{shop_id}/invites",
    response_model=ShopInviteResponse,
    summary="샵 초대코드 생성",
    description="샵에 초대코드를 생성합니다.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: COMMON_ERROR_RESPONSES[status.HTTP_403_FORBIDDEN],
        status.HTTP_409_CONFLICT: COMMON_ERROR_RESPONSES[status.HTTP_409_CONFLICT],
    },
)
def create_invite_link(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShopInviteResponse:
    return generate_invite_code_service(db=db, shop_id=shop_id, user=current_user)


@router.get(
    "/{shop_id}/invites",
    response_model=ShopInviteResponse,
    summary="샵 초대코드 조회",
    description="샵에 초대코드를 조회합니다.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: COMMON_ERROR_RESPONSES[status.HTTP_403_FORBIDDEN],
        status.HTTP_404_NOT_FOUND: COMMON_ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
    },
)
def get_invite_link(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShopInviteResponse:
    return get_invite_code_service(db=db, shop_id=shop_id, user=current_user)


@router.delete(
    "/{shop_id}/invites",
    summary="샵 초대코드 삭제",
    description="샵에 초대코드를 삭제합니다.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_403_FORBIDDEN: COMMON_ERROR_RESPONSES[status.HTTP_403_FORBIDDEN],
        status.HTTP_404_NOT_FOUND: COMMON_ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
    },
)
def delete_invite_link(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    return delete_invite_code_service(db=db, shop_id=shop_id, user=current_user)


@router.get(
    "/{shop_id}/users",
    response_model=list[ShopUserUserResponse],
    summary="샵 유저 목록 조회",
    description="특정 샵에 속한 유저 목록을 조회합니다.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_403_FORBIDDEN: COMMON_ERROR_RESPONSES[status.HTTP_403_FORBIDDEN],
        status.HTTP_404_NOT_FOUND: COMMON_ERROR_RESPONSES[status.HTTP_404_NOT_FOUND],
    },
)
def get_shop_users(
    shop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ShopUserUserResponse]:
    return get_shop_users_service(db=db, shop_id=shop_id, current_user=current_user)
