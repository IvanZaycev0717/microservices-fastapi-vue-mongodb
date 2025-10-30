import httpx

from settings import settings


async def send_ban_notification_webhook(email: str):
    """Send ban notification via webhook to notifications service.

    Args:
        email (str): Banned user's email address.
    """
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://{settings.ADMIN_SERVICE_HOST}:{settings.ADMIN_SERVICE_PORT}/notifications/ban",
            json={
                "email": email,
                "subject": "Блокировка аккаунта",
                "message": "Ваш аккаунт был заблокирован администратором",
            },
        )


async def send_delete_notification_webhook(email: str):
    """Send account deletion notification via webhook to notifications service.

    Args:
        email (str): Deleted user's email address.
    """
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://{settings.ADMIN_SERVICE_HOST}:{settings.ADMIN_SERVICE_PORT}/notifications/account-deleted",
            json={
                "email": email,
                "subject": "Удаление аккаунта",
                "message": "Ваш аккаунт и все данные были удалены",
            },
        )


async def send_ban_comments_webhook(user_id: str):
    """Send ban user comments notification via webhook to comments service.

    Args:
        user_id (str): ID of the banned user.
    """
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"http://{settings.ADMIN_SERVICE_HOST}:{settings.ADMIN_SERVICE_PORT}/comments/ban_user/{user_id}",
        )
