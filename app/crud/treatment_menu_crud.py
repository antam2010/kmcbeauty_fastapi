from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.treatment_menu import TreatmentMenu
from app.models.treatment_menu_detail import TreatmentMenuDetail


def create_treatment_menu(db: Session, name: str, shop_id: int) -> TreatmentMenu:
    return TreatmentMenu(
name=name,
        shop_id=shop_id,
    )


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
    shop_id: int,
    search: str = None,
) -> Page[TreatmentMenu]:
    query = (
        db.query(TreatmentMenu)
        .options(joinedload(TreatmentMenu.details))
        .filter(
            TreatmentMenu.shop_id == shop_id,
            TreatmentMenu.deleted_at.is_(None),
        )
    )

    if search:
        query = query.filter(
            or_(
                TreatmentMenu.name.ilike(f"%{search}%"),
                TreatmentMenu.details.any(
                    TreatmentMenuDetail.name.ilike(f"%{search}%"),
                ),
            ),
        )

    query.order_by(TreatmentMenu.id.desc())

    return paginate(query)


def get_treatment_menu_details_by_user(
    db: Session,
    menu_id: int,
    shop_id: int,
) -> list[TreatmentMenuDetail]:
    return (
        db.query(TreatmentMenuDetail)
        .join(TreatmentMenu, TreatmentMenuDetail.menu_id == TreatmentMenu.id)
        .filter(
            TreatmentMenuDetail.menu_id == menu_id,
            TreatmentMenu.shop_id == shop_id,
            TreatmentMenuDetail.deleted_at.is_(None),
        )
        .order_by(TreatmentMenuDetail.id.desc())
        .all()
    )


def get_menu_by_id(
    db: Session,
    menu_id: int,
    shop_id: int,
    exclude_deleted: bool = True,
) -> TreatmentMenu | None:
    query = db.query(TreatmentMenu).filter(
        TreatmentMenu.id == menu_id,
        TreatmentMenu.shop_id == shop_id,
    )
    if exclude_deleted:
        query = query.filter(TreatmentMenu.deleted_at.is_(None))

    return query.first()


def get_menu_detail_by_id(
    db: Session,
    menu_id: int,
    detail_id: int,
    shop_id: int,
) -> TreatmentMenuDetail | None:
    return (
        db.query(TreatmentMenuDetail)
        .filter(
            TreatmentMenuDetail.id == detail_id,
            TreatmentMenuDetail.menu_id == menu_id,
            TreatmentMenuDetail.deleted_at.is_(None),
        )
        .first()
    )
