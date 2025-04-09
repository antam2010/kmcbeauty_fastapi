from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.treatment_menu import TreatmentMenuCreate, TreatmentMenuDetailCreate
from app.services.treatment_menu_service import (
    create_treatment_menu,
    create_treatment_menu_detail,
)

router = APIRouter(prefix="/treatment-menus", tags=["시술 메뉴"])


@router.post("/")
def create_menu(
    data: TreatmentMenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # ✅ 타입도 명시
):
    return create_treatment_menu(name=data.name, user_id=current_user.id, db=db)


@router.post("/{menu_id}/details")
def create_menu_detail(
    menu_id: int,
    data: TreatmentMenuDetailCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_treatment_menu_detail(
        menu_id=menu_id,
        user_id=current_user.id,
        name=data.name,
        duration_min=data.duration_min,
        base_price=data.base_price,
        db=db,
    )
