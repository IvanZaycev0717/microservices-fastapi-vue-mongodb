import httpx

from settings import settings


async def send_ban_notification_webhook(email: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://{settings.BASE_HOST}:{settings.BASE_PORT}/notifications/ban",
            json={
                "email": email,
                "subject": "Блокировка аккаунта",
                "message": "Ваш аккаунт был заблокирован администратором",
            },
        )


async def send_delete_notification_webhook(email: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://{settings.BASE_HOST}:{settings.BASE_PORT}/notifications/account-deleted",
            json={
                "email": email,
                "subject": "Удаление аккаунта",
                "message": "Ваш аккаунт и все данные были удалены",
            },
        )


async def send_ban_comments_webhook(user_id: str):
    """Отправляет вебхук в comments service для бана комментариев пользователя"""
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"http://{settings.BASE_HOST}:{settings.BASE_PORT}/comments/ban_user/{user_id}",
        )
