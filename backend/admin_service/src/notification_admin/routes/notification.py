import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from content_admin.dependencies import get_logger_factory
from notification_admin.crud.notification import NotificationCRUD
from notification_admin.dependecies import get_notification_db
from notification_admin.models.notification import (
    NotificationCreate,
    NotificationResponse,
)
from notification_admin.tasks import send_email_task
from settings import settings

router = APIRouter(prefix="/notifications")


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
