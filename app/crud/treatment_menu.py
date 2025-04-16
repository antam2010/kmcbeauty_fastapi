from sqlalchemy.orm import Session, joinedload

from app.models.treatment_menu import TreatmentMenu
from app.models.treatment_menu_detail import TreatmentMenuDetail


def create_treatment_menu(db: Session, name: str, user_id: int) -> TreatmentMenu:
    menu = TreatmentMenu(name=name, user_id=user_id)
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


def create_treatment_menu_detail(
    db: Session,
    menu_id: int,
    name: str,
    duration_min: int,
    base_price: int,
) -> TreatmentMenuDetail:
    detail = TreatmentMenuDetail(
        menu_id=menu_id,
        name=name,
        duration_min=duration_min,
        base_price=base_price,
    )
    db.add(detail)
    db.commit()
    db.refresh(detail)
    return detail


def get_treatment_menus_by_user(
    db: Session,
    user_id: int,
    name: str = None,
) -> list[TreatmentMenu]:
    query = db.query(TreatmentMenu).options(
        joinedload(TreatmentMenu.details)
    ).filter(
        TreatmentMenu.user_id == user_id
    )

    if name:
        query = query.filter(TreatmentMenu.name == name)

    return query.order_by(TreatmentMenu.id.desc())


def get_treatment_menu_details_by_user(
    db: Session,
    menu_id: int,
    user_id: int,
) -> list[TreatmentMenuDetail]:
    return (
        db.query(TreatmentMenuDetail)
        .join(TreatmentMenu, TreatmentMenuDetail.menu_id == TreatmentMenu.id)
        .filter(
            TreatmentMenuDetail.menu_id == menu_id,
            TreatmentMenu.user_id == user_id,
            TreatmentMenuDetail.deleted_at.is_(None)
        )
        .order_by(TreatmentMenuDetail.created_at.desc())
        .all()
    )
