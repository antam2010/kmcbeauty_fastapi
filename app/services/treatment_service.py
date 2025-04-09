from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.treatment import Treatment
from app.models.treatment_item import TreatmentItem
from app.models.treatment_menu_detail import TreatmentMenuDetail
from app.models.user import User
from app.schemas.treatment import TreatmentCreate


def create_treatment(
    data: TreatmentCreate, db: Session, current_user: User
) -> Treatment:
    # 실제 받은 금액 (프론트에서 입력한 total_price)
    treatment = Treatment(
        user_id=current_user.id,
        phonebook_id=data.phonebook_id,
        reserved_at=data.reserved_at,
        memo=data.memo,
        total_price=data.total_price,  # 실제 결제된 금액
        status=data.status,
    )
    db.add(treatment)
    db.flush()

    for item in data.items:
        menu_detail = (
            db.query(TreatmentMenuDetail).filter_by(id=item.menu_detail_id).first()
        )
        if not menu_detail:
            raise HTTPException(
                status_code=400,
                detail=f"시술 항목 {item.menu_detail_id}이 존재하지 않음",
            )

        db.add(
            TreatmentItem(
                treatment_id=treatment.id,
                menu_detail_id=menu_detail.id,
            )
        )

    db.commit()
    db.refresh(treatment)

    return get_treatment_by_id(treatment.id, db)


def get_treatment_by_id(treatment_id: int, db: Session) -> Treatment:
    treatment = (
        db.query(Treatment)
        .options(joinedload(Treatment.items))
        .filter(Treatment.id == treatment_id)
        .first()
    )
    if not treatment:
        raise HTTPException(status_code=404, detail="시술 예약을 찾을 수 없습니다.")
    return treatment
