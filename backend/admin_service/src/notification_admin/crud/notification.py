from datetime import datetime

from bson import ObjectId
from bson.errors import BSONError
from pymongo import DESCENDING
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from notification_admin.models.notification import NotificationCreate


class NotificationCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection = db.notifications

    # CREATE
    async def create(self, notification: NotificationCreate) -> str:
        """Создает уведомление в базе и возвращает его ID"""
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
        try:
            cursor = self.collection.find().sort("created_at", DESCENDING)
            notifications = await cursor.to_list(length=100)
            return notifications
        except Exception as e:
            raise

    async def get_by_email(self, email: str) -> list[dict]:
        cursor = self.collection.find({"to_email": email})
        return await cursor.to_list(length=100)

    # UPDATE
    async def update_status(self, notification_id: str, status: str) -> bool:
        """Обновляет статус уведомления"""
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
        """Удаляет уведомление по ID"""
        result = await self.collection.delete_one(
            {"_id": ObjectId(notification_id)}
        )
        return result.deleted_count > 0
