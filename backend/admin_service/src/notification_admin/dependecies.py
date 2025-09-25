from fastapi import HTTPException, Request, status
from pymongo.asynchronous.database import AsyncDatabase


async def get_notification_db(request: Request) -> AsyncDatabase:
    """Зависимость для получения notification admin MongoDB базы"""
    try:
        return request.app.state.notification_admin_db
    except AttributeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Notification database service unavailable",
        )
