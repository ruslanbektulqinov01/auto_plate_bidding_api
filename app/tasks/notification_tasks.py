# app/tasks/notification_tasks.py
from sqlalchemy import select

from app.core.celery_app import celery_app
from app.database import async_session_factory
from app.models.user import User
from app.models.plate import AutoPlate
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="send_bid_notification")
def send_bid_notification(plate_id: int, user_id: int, amount: float):
    """
    Celery task to send bid notifications
    Note: Celery tasks should be synchronous, so we handle the async operations differently
    """
    try:
        import asyncio
        from sqlalchemy import select

        # Run the async notification logic in a new event loop
        return asyncio.run(_send_notification_async(plate_id, user_id, amount))

    except Exception as e:
        logger.error(f"Error sending bid notification: {str(e)}")
        return False


async def _send_notification_async(plate_id: int, user_id: int, amount: float) -> bool:
    """Internal async function to handle the notification logic"""
    async with async_session_factory() as session:
        try:
            # Use SQLAlchemy 2.0 style queries
            plate_query = select(AutoPlate).where(AutoPlate.id == plate_id)
            user_query = select(User).where(User.id == user_id)

            plate_result = await session.execute(plate_query)
            user_result = await session.execute(user_query)

            plate = plate_result.scalar_one_or_none()
            user = user_result.scalar_one_or_none()

            if not plate or not user:
                logger.error(f"Could not find plate (id={plate_id}) or user (id={user_id})")
                return False

            # Here you would implement actual notification logic
            # This could be sending an email, push notification, etc.

            # Example of what notification might contain:
            notification_content = {
                "title": f"Bid Placed on {plate.plate_number}",
                "message": f"You placed a bid of ${amount} on plate {plate.plate_number}.",
                "user_id": user_id,
                "plate_id": plate_id
            }

            logger.info(f"Notification sent: {notification_content}")
            # Here you would send through your notification service
            # e.g., I want to send a push notification to the user using Websocket



            return True

        except Exception as e:
            logger.error(f"Error in async notification process: {str(e)}")
            return False
