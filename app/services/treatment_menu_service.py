from sqlalchemy.orm import Session
from app.models.treatment_menu import TreatmentMenu
from app.models.treatment_menu_detail import TreatmentMenuDetail


def create_treatment_menu(name: str, user_id: int, db: Session) -> TreatmentMenu:
    menu = TreatmentMenu(name=name, user_id=user_id)
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


def create_treatment_menu_detail(menu_id: int, user_id: int, name: str, duration_min: int, base_price: int, db: Session) -> TreatmentMenuDetail:
    detail = TreatmentMenuDetail(
        menu_id=menu_id,
        user_id=user_id,
        name=name,
        duration_min=duration_min,
        base_price=base_price,
    )
    db.add(detail)
    db.commit()
    db.refresh(detail)
    return detail
