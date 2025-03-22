# app/tasks/user_tasks.py
from app.core.celery_app import celery_app
from app.database import get_session
from app.models.user import User
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)



@celery_app.task(name="user_activity_report")
def generate_user_activity_report():
    """
    Example periodic task that generates a report of user activity
    """
    logger.info("Generating user activity report")
    # Report generation logic would go here
    return True