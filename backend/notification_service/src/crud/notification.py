from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.asynchronous.database import AsyncDatabase

from models.notification import NotificationCreate


class NotificationCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection = db.notifications

    async def create(
        self, notification: NotificationCreate, subject: str, message: str
    ) -> str:
        """Create a new notification in the database.

        Args:
            notification: Notification data from Kafka message
            subject: Email subject
            message: Email message content

        Returns:
            str: String representation of the inserted notification's ID
        """
        notification_data = {
            "to_email": notification.email,
            "subject": subject,
            "message": message,
            "status": "pending",
            "message_type": notification.message_type,
            "user_id": notification.user_id,
            "created_at": datetime.now(),
        }

        result = await self.collection.insert_one(notification_data)
        return str(result.inserted_id)

    async def update_status(self, notification_id: str, status: str) -> bool:
        """Update notification status and sent timestamp.

        Args:
            notification_id: ID of the notification to update
            status: New status for the notification

        Returns:
            bool: True if notification was successfully updated, False otherwise
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {"status": status, "sent_at": datetime.now()}},
            )
            return result.modified_count > 0
        except InvalidId:
            return False
        except Exception:
            return False

    async def get_pending_notifications(self) -> list[dict]:
        """Retrieve all pending notifications.

        Returns:
            list[dict]: List of pending notifications
        """
        cursor = self.collection.find({"status": "pending"})
        return await cursor.to_list(length=100)
