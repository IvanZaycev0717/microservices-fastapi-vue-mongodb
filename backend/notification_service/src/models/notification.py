from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class NotificationCreate(BaseModel):
    """Request model for creating notifications from Kafka messages.

    Attributes:
        email: Recipient email address
        reset_token: Password reset token (for reset requests)
        user_id: User identifier
        message_type: Type of notification (reset_request/reset_success)
    """

    email: EmailStr
    reset_token: str | None = None
    user_id: str
    message_type: str = Field(pattern="^(reset_request|reset_success)$")


class NotificationResponse(BaseModel):
    """Response model for notification data stored in MongoDB.

    Attributes:
        id: Notification identifier
        to_email: Recipient email address
        subject: Email subject
        message: Email message content
        status: Current notification status
        created_at: Creation timestamp
        sent_at: Sent timestamp if applicable
        message_type: Type of notification
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    to_email: EmailStr
    subject: str
    message: str
    status: str = Field(pattern="^(pending|sent|failed)$")
    created_at: datetime
    sent_at: datetime | None = None
    message_type: str

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        return str(v)
