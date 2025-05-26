from datetime import timedelta

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.treatment import get_treatments_to_autocomplete
from app.database import SessionLocal
from app.exceptions import CustomException
from app.models.treatment import Treatment
from app.utils.datetime import now_kst
from celery_app import celery_app

DOMAIN = "treatment_task"


@celery_app.task
def auto_complete_treatment() -> None:
    db: Session = SessionLocal()
    try:
        now = now_kst().replace(tzinfo=None)

        rows = get_treatments_to_autocomplete(db)

        # 완료 대상만 필터링
        complete_ids = [
            row.treatment_id
            for row in rows
            if now >= row.reserved_at + timedelta(minutes=float(row.total_duration_min))
        ]

        if complete_ids:
            db.query(Treatment).filter(Treatment.id.in_(complete_ids)).update(
                {
                    Treatment.status: "COMPLETED",
                    Treatment.finished_at: now,
                },
                synchronize_session=False,  # 중요, ORM 상태 추적없이 곧바로 sql 만 실행
            )

        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise CustomException(
            status_code=500,
            domain=DOMAIN,
            exception=e,
        ) from e
    except Exception as e:
        db.rollback()
        raise CustomException(
            status_code=500,
            domain=DOMAIN,
            exception=e,
        ) from e
    finally:
        db.close()
