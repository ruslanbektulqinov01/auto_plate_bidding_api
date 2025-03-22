# app/core/celery_app.py
from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "app",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.notification_tasks", "app.tasks.user_tasks"]  # Include both task modules
)

# Optional Celery configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# This allows you to call tasks directly from your app code
def get_celery_app() -> Celery:
    return celery_app