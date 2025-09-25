import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import EmailStr
from pymongo.asynchronous.database import AsyncDatabase

from content_admin.dependencies import get_logger_factory
from notification_admin.crud.notification import NotificationCRUD
from notification_admin.dependecies import get_notification_db
from notification_admin.models.notification import (
    BanNotification,
    NotificationCreate,
    NotificationResponse,
)
from notification_admin.tasks import send_email_task
from settings import settings

router = APIRouter(prefix="/notifications")


@router.get("/", response_model=list[NotificationResponse])
async def get_all_notifications(
    db: Annotated[AsyncDatabase, Depends(get_notification_db)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.NOTIFICATION_ADMIN_NAME)),
    ],
):
    """Получить все уведомления"""
    try:
        crud = NotificationCRUD(db)
        notifications_data = await crud.get_all()

        notifications = [
            NotificationResponse(**notification)
            for notification in notifications_data
        ]

        return notifications

    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting notifications",
        )


@router.get("/by-email/{email}", response_model=list[NotificationResponse])
async def get_notifications_by_email(
    email: EmailStr,
    db: Annotated[AsyncDatabase, Depends(get_notification_db)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.NOTIFICATION_ADMIN_NAME)),
    ],
):
    """Получить все уведомления по email получателя"""
    try:
        crud = NotificationCRUD(db)
        notifications_data = await crud.get_by_email(email)

        if not notifications_data:
            logger.info(f"No notifications found for {email}")
            raise HTTPException(
                status_code=404, detail="No notifications found"
            )

        logger.info(
            f"Found {len(notifications_data)} notifications for {email}"
        )
        return [NotificationResponse(**n) for n in notifications_data]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notifications for {email}: {e}")
        raise HTTPException(
            status_code=500, detail="Error getting notifications"
        )


@router.post("", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.NOTIFICATION_ADMIN_NAME)),
    ],
    db: Annotated[AsyncDatabase, Depends(get_notification_db)],
):
    crud = NotificationCRUD(db)

    try:
        notification_id = await crud.create(notification)
        logger.info(f"Notification created successfully: {notification_id}")

        if settings.IS_SEND_EMAIL_ENABLED:
            background_tasks.add_task(
                send_email_task,
                notification_id,
                notification.to_email,
                notification.subject,
                notification.message,
                db,
            )

        return NotificationResponse(
            id=notification_id,
            to_email=notification.to_email,
            subject=notification.subject,
            message=notification.message,
            status="pending",
            created_at=datetime.now(),
        )

    except ValueError as e:
        logger.warning(f"Validation error creating notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    db: Annotated[AsyncDatabase, Depends(get_notification_db)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.NOTIFICATION_ADMIN_NAME)),
    ],
):
    """Удалить уведомление по ID"""
    try:
        crud = NotificationCRUD(db)
        deleted = await crud.delete(notification_id)

        if not deleted:
            raise HTTPException(
                status_code=404, detail="Notification not found"
            )

        logger.info(f"Notification {notification_id} deleted successfully")
        return {"message": "Notification deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification {notification_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Error deleting notification"
        )


@router.post("/ban")
async def ban_notification(
    ban_data: BanNotification,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncDatabase, Depends(get_notification_db)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.NOTIFICATION_ADMIN_NAME)),
    ],
):
    """Эндпоинт для получения вебхука о блокировке пользователя"""
    try:
        notification = NotificationCreate(
            to_email=ban_data.email,
            subject=ban_data.subject,
            message=ban_data.message,
        )

        crud = NotificationCRUD(db)
        notification_id = await crud.create(notification)
        logger.info(f"Ban notification created for {ban_data.email}")

        if settings.IS_SEND_EMAIL_ENABLED:
            background_tasks.add_task(
                send_email_task,
                notification_id,
                ban_data.email,
                ban_data.subject,
                ban_data.message,
                db,
            )

        return {"message": "Ban notification created"}

    except Exception as e:
        logger.error(f"Error creating ban notification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/account-deleted")
async def account_deleted_notification(
    notification_data: BanNotification,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncDatabase, Depends(get_notification_db)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.NOTIFICATION_ADMIN_NAME)),
    ],
):
    """Эндпоинт для получения вебхука об удалении аккаунта пользователя"""
    try:
        notification = NotificationCreate(
            to_email=notification_data.email,
            subject=notification_data.subject,
            message=notification_data.message,
        )

        crud = NotificationCRUD(db)
        notification_id = await crud.create(notification)
        logger.info(
            f"Account deletion notification created for {notification_data.email}"
        )

        if settings.IS_SEND_EMAIL_ENABLED:
            background_tasks.add_task(
                send_email_task,
                notification_id,
                notification_data.email,
                notification_data.subject,
                notification_data.message,
                db,
            )

        return {"message": "Account deletion notification created"}

    except Exception as e:
        logger.error(f"Error creating account deletion notification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
