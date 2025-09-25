from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class NotificationCreate(BaseModel):
    to_email: EmailStr  # получатель письма
    subject: str = Field(min_length=1, max_length=200)  # тема письма
    message: str = Field(min_length=1)  # сообщение письма


class NotificationResponse(BaseModel):
    """Модель ответа API"""

    id: str
    to_email: EmailStr
    subject: str
    message: str
    status: str
    created_at: datetime
    sent_at: datetime | None = None
