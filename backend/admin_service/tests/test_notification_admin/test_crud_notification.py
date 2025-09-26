from datetime import datetime

from bson import ObjectId

from src.notification_admin.models.notification import NotificationCreate


class TestNotificationCRUD:
    async def test_create_notification(self, notification_crud, fake):
        notification_data = NotificationCreate(
            to_email=fake.person.email(),
            subject=fake.text.word()[:50],
            message=fake.text.text()[:200],
        )

        notification_id = await notification_crud.create(notification_data)

        assert notification_id is not None
        assert ObjectId.is_valid(notification_id)

    async def test_create_notification_has_correct_data(
        self, notification_crud, fake
    ):
        email = fake.person.email()
        subject = "Test Subject"
        message = "Test message content"

        notification_data = NotificationCreate(
            to_email=email, subject=subject, message=message
        )

        notification_id = await notification_crud.create(notification_data)

        notification = await notification_crud.collection.find_one(
            {"_id": ObjectId(notification_id)}
        )

        assert notification["to_email"] == email
        assert notification["subject"] == subject
        assert notification["message"] == message
        assert notification["status"] == "pending"
        assert isinstance(notification["created_at"], datetime)

    async def test_get_all_notifications(self, notification_crud, fake):
        for i in range(3):
            notification_data = NotificationCreate(
                to_email=f"user{i}@test.com",
                subject=f"Subject {i}",
                message=f"Message {i}",
            )
            await notification_crud.create(notification_data)

        notifications = await notification_crud.get_all()
        assert len(notifications) == 3

    async def test_get_all_notifications_empty(self, notification_crud):
        notifications = await notification_crud.get_all()
        assert len(notifications) == 0

    async def test_get_by_email(self, notification_crud, fake):
        target_email = "target@test.com"
        other_email = "other@test.com"

        for i in range(2):
            notification_data = NotificationCreate(
                to_email=target_email,
                subject=f"Subject {i}",
                message=f"Message {i}",
            )
            await notification_crud.create(notification_data)

        notification_data = NotificationCreate(
            to_email=other_email,
            subject="Other subject",
            message="Other message",
        )
        await notification_crud.create(notification_data)

        notifications = await notification_crud.get_by_email(target_email)
        assert len(notifications) == 2
        assert all(
            notification["to_email"] == target_email
            for notification in notifications
        )

    async def test_get_by_email_not_found(self, notification_crud):
        notifications = await notification_crud.get_by_email(
            "nonexistent@test.com"
        )
        assert len(notifications) == 0

    async def test_update_status_success(self, notification_crud, fake):
        notification_data = NotificationCreate(
            to_email=fake.person.email(),
            subject="Test Subject",
            message="Test message",
        )
        notification_id = await notification_crud.create(notification_data)

        updated = await notification_crud.update_status(
            notification_id, "sent"
        )
        assert updated is True

        notification = await notification_crud.collection.find_one(
            {"_id": ObjectId(notification_id)}
        )
        assert notification["status"] == "sent"
        assert isinstance(notification["sent_at"], datetime)

    async def test_update_status_invalid_id(self, notification_crud):
        updated = await notification_crud.update_status("invalid_id", "sent")
        assert updated is False

    async def test_update_status_not_found(self, notification_crud):
        updated = await notification_crud.update_status(
            str(ObjectId()), "sent"
        )
        assert updated is False

    async def test_delete_notification(self, notification_crud, fake):
        notification_data = NotificationCreate(
            to_email=fake.person.email(),
            subject="Test Subject",
            message="Test message",
        )
        notification_id = await notification_crud.create(notification_data)

        deleted = await notification_crud.delete(notification_id)
        assert deleted is True

        notification = await notification_crud.collection.find_one(
            {"_id": ObjectId(notification_id)}
        )
        assert notification is None

    async def test_delete_notification_invalid_id(self, notification_crud):
        deleted = await notification_crud.delete("invalid_id")
        assert deleted is False

    async def test_delete_notification_not_found(self, notification_crud):
        deleted = await notification_crud.delete(str(ObjectId()))
        assert deleted is False
