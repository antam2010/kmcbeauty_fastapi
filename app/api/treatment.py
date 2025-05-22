from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.shop import get_current_shop
from app.docs.common_responses import COMMON_ERROR_RESPONSES
from app.models.user import User
from app.schemas.treatment import (
    TreatmentCreate,
    TreatmentDetail,
    TreatmentFilter,
    TreatmentResponse,
)
from app.services.treatment_service import (
    create_treatment_service,
    get_treatment_list_service,
    update_treatment_service,
)

router = APIRouter(prefix="/treatments", tags=["시술 예약"])


# 시술 예약 생성
@router.post(
    "",
    response_model=TreatmentResponse,
    summary="시술 예약 생성",
    description="시술 예약을 생성합니다.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: COMMON_ERROR_RESPONSES[
            status.HTTP_400_BAD_REQUEST
        ],
        status.HTTP_500_INTERNAL_SERVER_ERROR: COMMON_ERROR_RESPONSES[
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ],
    },
)
def create_treatment_api(
    data: TreatmentCreate,
    db: Session = Depends(get_db),
    current_shop: User = Depends(get_current_shop),
) -> TreatmentResponse:
    return create_treatment_service(data, db, current_shop)


@router.put(
    "/{treatment_id}",
    response_model=TreatmentResponse,
    summary="시술 예약 수정",
    description="시술 예약을 수정합니다.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: COMMON_ERROR_RESPONSES[
            status.HTTP_400_BAD_REQUEST
        ],
        status.HTTP_500_INTERNAL_SERVER_ERROR: COMMON_ERROR_RESPONSES[
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ],
    },
)
def update_treatment_api(
    treatment_id: int,
    data: TreatmentCreate,
    db: Session = Depends(get_db),
    current_shop: User = Depends(get_current_shop),
) -> TreatmentResponse:
    return update_treatment_service(
        data=data,
        db=db,
        current_shop=current_shop,
        treatment_id=treatment_id,
    )


# 시술 예약 목록 조회
@router.get(
    "",
    response_model=Page[TreatmentDetail],
    summary="시술 예약 목록 조회",
    description="시술 예약 목록을 조회합니다.",
    status_code=status.HTTP_200_OK,
)
def list_treatments_api(
    db: Session = Depends(get_db),
    current_shop: User = Depends(get_current_shop),
    filters: TreatmentFilter = Depends(),
) -> Page[TreatmentDetail]:
    return get_treatment_list_service(
        db=db,
        current_shop=current_shop,
        filters=filters,
    )
