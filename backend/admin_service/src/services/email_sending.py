from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from settings import settings


def get_email_config() -> ConnectionConfig:
    """Get email configuration for FastAPI-Mail.

    Returns:
        ConnectionConfig: Email connection configuration object.
    """
    return ConnectionConfig(
        MAIL_USERNAME=settings.SMTP_USERNAME.get_secret_value(),
        MAIL_PASSWORD=settings.SMTP_PASSWORD.get_secret_value(),
        MAIL_FROM=settings.SMTP_FROM.get_secret_value(),
        MAIL_PORT=settings.SMTP_PORT,
        MAIL_SERVER=settings.SMTP_SERVER,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )


async def send_email(to_email: str, subject: str, message: str) -> bool:
    """Send email using FastAPI-Mail service.

    Args:
        to_email (str): Recipient email address.
        subject (str): Email subject.
        message (str): Email message content.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    try:
        conf = get_email_config()
        email_message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=message,
            subtype=MessageType.plain,
        )

        fm = FastMail(conf)
        await fm.send_message(email_message)
        return True

    except Exception:
        return False
