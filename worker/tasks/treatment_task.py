from datetime import timedelta

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.crud.treatment_crud import get_treatments_to_autocomplete
from app.database import SessionLocal
from app.exceptions import CustomException
from app.models.treatment import Treatment
from app.utils.datetime import now_utc
from celery_app import celery_app

DOMAIN = "treatment_task"


# @MX:WARN: [AUTO] 자동완료 판정은 타임존/NULL 경계에 민감하다.
# @MX:REASON: (1) reserved_at 는 naive DateTime 컬럼이며 저장 규약이 UTC(앱이 UTC ISO
#             전송, 서버 TimestampMixin/SoftDeleteMixin 모두 UTC 사용)이므로 비교 기준을
#             반드시 UTC-naive 로 맞춰야 한다. 이전 now_kst().replace(tzinfo=None) 는
#             KST-naive 로 9시간 어긋나 오판정을 유발했다(SPEC-FIX-001 REQ-FIX-004).
#             (2) 항목 없는 시술은 total_duration_min(SUM)이 None 이라 float(None)
#             크래시 위험이 있으므로 None 은 건너뛴다.
@celery_app.task
def auto_complete_treatment() -> None:
    db: Session = SessionLocal()
    try:
        # reserved_at 는 UTC-naive 로 저장되므로 비교 기준도 UTC-naive 로 정규화한다.
        now = now_utc().replace(tzinfo=None)

        rows = get_treatments_to_autocomplete(db)

        # 완료 대상만 필터링.
        # total_duration_min 이 None(항목 없는 시술)이면 종료 시각을 계산할 수
        # 없으므로 크래시 없이 건너뛴다(COALESCE 대신 스킵 — 항목 없는 예약은
        # 자동완료 대상 아님).
        complete_ids = [
            row.treatment_id
            for row in rows
            if row.total_duration_min is not None
            and now
            >= row.reserved_at + timedelta(minutes=float(row.total_duration_min))
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
