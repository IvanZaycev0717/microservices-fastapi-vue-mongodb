from fastapi import HTTPException, Request, status
from pymongo.asynchronous.database import AsyncDatabase


async def get_notification_db(request: Request) -> AsyncDatabase:
    """Get notification database instance from application state.

    Args:
        request: FastAPI Request object containing application state.

    Returns:
        AsyncDatabase: Async database instance for notifications.

    Raises:
        HTTPException: If notification database service is unavailable.
    """
    try:
        return request.app.state.notification_admin_db
    except AttributeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Notification database service unavailable",
        )
