import logging
from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Path,
    status,
)
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


@router.get("", response_model=list[NotificationResponse])
async def get_all_notifications(
    db: Annotated[AsyncDatabase, Depends(get_notification_db)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.NOTIFICATION_ADMIN_NAME)),
    ],
):
    """Retrieve all notifications from the system.

    Args:
        db: Injected async database dependency.
        logger: Injected logger instance for notification admin.

    Returns:
        list[NotificationResponse]: List of notification responses.

    Raises:
        HTTPException: If internal error occurs while fetching notifications.
    """
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
    """Retrieve notifications for a specific email address.

    Args:
        email: Email address to filter notifications by.
        db: Injected async database dependency.
        logger: Injected logger instance for notification admin.

    Returns:
        list[NotificationResponse]: List of notification responses for the email.

    Raises:
        HTTPException: If no notifications found or internal error occurs.
    """
    try:
        crud = NotificationCRUD(db)
        notifications_data = await crud.get_by_email(email)

        if not notifications_data:
            logger.info(f"No notifications found for {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No notifications found",
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting notifications",
        )


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_notification(
    notification: NotificationCreate,
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.NOTIFICATION_ADMIN_NAME)),
    ],
    db: Annotated[AsyncDatabase, Depends(get_notification_db)],
):
    """Create a new notification.

    Args:
        notification: Notification data to create.
        logger: Injected logger instance for notification admin.
        db: Injected async database dependency.

    Returns:
        NotificationResponse: Created notification response.

    Raises:
        HTTPException: If validation fails or internal error occurs.
    """
    crud = NotificationCRUD(db)

    try:
        notification_id = await crud.create(notification)
        logger.info(f"Notification created successfully: {notification_id}")

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
    notification_id: Annotated[
        str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)
    ],
    db: Annotated[AsyncDatabase, Depends(get_notification_db)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.NOTIFICATION_ADMIN_NAME)),
    ],
):
    """Delete a specific notification by ID.

    Args:
        notification_id: ID of the notification to delete.
        db: Injected async database dependency.
        logger: Injected logger instance for notification admin.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If notification not found or internal error occurs.
    """
    try:
        crud = NotificationCRUD(db)
        deleted = await crud.delete(notification_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )

        logger.info(f"Notification {notification_id} deleted successfully")
        return {"message": "Notification deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification {notification_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting notification",
        )


# WEBHOOKS USING ONLY
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
    """Create a ban notification and optionally send email.

    Args:
        ban_data: Ban notification data.
        background_tasks: FastAPI background tasks for async operations.
        db: Injected async database dependency.
        logger: Injected logger instance for notification admin.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If internal error occurs.
    """
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


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
    """Create an account deletion notification and optionally send email.

    Args:
        notification_data: Account deletion notification data.
        background_tasks: FastAPI background tasks for async operations.
        db: Injected async database dependency.
        logger: Injected logger instance for notification admin.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If internal error occurs.
    """
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
