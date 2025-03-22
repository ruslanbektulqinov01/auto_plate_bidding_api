# app/core/celery_beat.py
from app.core.celery_app import celery_app
from celery.schedules import crontab

# Define periodic tasks
celery_app.conf.beat_schedule = {
}
