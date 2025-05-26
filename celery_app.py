from celery import Celery
from celery.schedules import crontab

from app.core.config import APP_ENV

# 환경에 따라 Redis URL 구성
redis_url = "redis://localhost:6379/0" if APP_ENV == "debug" else "redis://redis:6379/0"

celery_app = Celery(
    "worker",
    broker=redis_url,
    backend=redis_url,
    include=["worker.tasks.treatment_task"],
)

celery_app.conf.timezone = "Asia/Seoul"


celery_app.conf.beat_schedule = {
    "auto-complete-treatment-every-5min": {
        "task": "worker.tasks.treatment_task.auto_complete_treatment",
        "schedule": crontab(minute="*/30"),
    },
}
