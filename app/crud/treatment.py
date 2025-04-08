from app.models.treatment import Treatment
from app.schemas.treatment import TreatmentCreate, TreatmentItemCreate
from sqlalchemy.orm import Session, joinedload

def create_treatment(data: TreatmentCreate, db: Session):
    total_price = sum(item.price for item in data.items)
    treatment = Treatment(
        phonebook_id=data.phonebook_id,
        reserved_at=data.reserved_at,
        memo=data.memo,
        total_price=total_price,
        status="RESERVED"
    )
    db.add(treatment)
    db.flush()  # treatment.id 확보

    for item in data.items:
        db.add(TreatmentItemCreate(
            treatment_id=treatment.id,
            menu_detail_id=item.menu_detail_id,
            name=item.name,
            price=item.price,
            duration_min=item.duration_min
        ))
    db.commit()
    db.refresh(treatment)
    return treatment
