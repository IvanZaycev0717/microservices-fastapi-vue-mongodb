from pymongo.asynchronous.database import AsyncDatabase

from notification_admin.crud.notification import NotificationCRUD
from services.email_sending import send_email


async def send_email_task(
    notification_id: str,
    to_email: str,
    subject: str,
    message: str,
    db: AsyncDatabase,
):
    """Background task to send email and update notification status.

    Args:
        notification_id (str): ID of the notification to update.
        to_email (str): Recipient email address.
        subject (str): Email subject.
        message (str): Email message content.
        db (AsyncDatabase): Async database instance.
    """
    try:
        crud = NotificationCRUD(db)

        success = await send_email(to_email, subject, message)

        if success:
            await crud.update_status(notification_id, "sent")
        else:
            await crud.update_status(notification_id, "failed")

    except Exception:
        pass
