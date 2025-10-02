from datetime import datetime

from bson import ObjectId
from bson.errors import BSONError, InvalidId
from pymongo import DESCENDING
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from notification_admin.models.notification import NotificationCreate


class NotificationCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection = db.notifications

    # CREATE
    async def create(self, notification: NotificationCreate) -> str:
        """Create a new notification in the database.

        Args:
            notification (NotificationCreate): Notification data to create.

        Returns:
            str: String representation of the inserted notification's ID.

        Raises:
            ValueError: If notification already exists or data format is invalid.
        """
        try:
            notification_data = {
                "to_email": notification.to_email,
                "subject": notification.subject,
                "message": notification.message,
                "status": "pending",
                "created_at": datetime.now(),
            }

            result = await self.collection.insert_one(notification_data)
            return str(result.inserted_id)

        except DuplicateKeyError as e:
            raise ValueError(f"Notification already exists: {e}")
        except BSONError as e:
            raise ValueError(f"Invalid data format: {e}")

    # READ
    async def get_all(self) -> list[dict]:
        """Retrieve all notifications from the database.

        Returns:
            list[dict]: List of notifications sorted by creation date descending.

        Raises:
            Exception: If database operation fails.
        """
        try:
            cursor = self.collection.find().sort("created_at", DESCENDING)
            notifications = await cursor.to_list(length=100)
            return notifications
        except Exception as e:
            raise

    async def get_by_email(self, email: str) -> list[dict]:
        """Retrieve notifications for a specific email address.

        Args:
            email (str): Email address to filter notifications by.

        Returns:
            list[dict]: List of notifications for the specified email.
        """
        cursor = self.collection.find({"to_email": email})
        return await cursor.to_list(length=100)

    # UPDATE
    async def update_status(self, notification_id: str, status: str) -> bool:
        """Update notification status and sent timestamp.

        Args:
            notification_id (str): ID of the notification to update.
            status (str): New status for the notification.

        Returns:
            bool: True if notification was successfully updated, False otherwise.
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {"status": status, "sent_at": datetime.now()}},
            )
            return result.modified_count > 0
        except Exception as e:
            return False

    # DELETE
    async def delete(self, notification_id: str) -> bool:
        """Delete a notification by ID.

        Args:
            notification_id (str): ID of the notification to delete.

        Returns:
            bool: True if notification was successfully deleted, False otherwise.
        """
        try:
            result = await self.collection.delete_one(
                {"_id": ObjectId(notification_id)}
            )
            return result.deleted_count > 0
        except InvalidId:
            return False
