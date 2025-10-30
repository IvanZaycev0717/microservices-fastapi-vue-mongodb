import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from logger import get_logger
from services.database import db_manager
from services.email_templates import email_templates
from settings import settings

logger = get_logger("EmailSending")


async def send_email(to_email: str, subject: str, html_message: str) -> bool:
    """Sends an HTML email asynchronously.

    Constructs and sends an HTML formatted email using SMTP.

    Args:
        to_email: Recipient email address.
        subject: Email subject line.
        html_message: HTML content of the email.

    Returns:
        bool: True if email was sent successfully, False otherwise.

    Note:
        - Uses SMTP settings from application configuration
        - Runs synchronous SMTP operations in executor to avoid blocking
        - Logs errors but returns False instead of raising exceptions
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_FROM.get_secret_value()
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_message, "html"))

        success = await asyncio.get_event_loop().run_in_executor(
            None, lambda: _send_sync_email(msg, to_email)
        )
        return success

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def _send_sync_email(msg: MIMEMultipart, to_email: str) -> bool:
    """Synchronously sends an email via SMTP SSL.

    Handles the actual SMTP connection, authentication, and email sending.

    Args:
        msg: MIMEMultipart object containing the email message.
        to_email: Recipient email address for logging purposes.

    Returns:
        bool: True if email was sent successfully, False otherwise.

    Note:
        - Uses SMTP_SSL for secure connection
        - Authenticates with credentials from application settings
        - Converts message to string format for transmission
        - Properly closes SMTP connection after sending
        - Logs success and failure outcomes
    """
    try:
        server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)

        server.login(
            settings.SMTP_USERNAME.get_secret_value(),
            settings.SMTP_PASSWORD.get_secret_value(),
        )

        text = msg.as_string()
        server.sendmail(settings.SMTP_FROM.get_secret_value(), to_email, text)
        server.quit()

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"SMTP error sending to {to_email}: {e}")
        return False


async def send_notification_email(
    notification_id: str,
    to_email: str,
    message_type: str,
    reset_token: str = None,
):
    """Sends notification email based on message type and updates notification status.

    Processes different types of email notifications (password reset requests and
    success confirmations) with fallback content if template rendering fails.

    Args:
        notification_id: Unique identifier for the notification record.
        to_email: Recipient email address.
        message_type: Type of notification ('reset_request' or 'reset_success').
        reset_token: Password reset token (required for 'reset_request' type).

    Note:
        - Uses email templates for proper HTML formatting
        - Provides fallback content if template rendering fails
        - Updates notification status in database after sending attempt
        - Handles both successful and failed email delivery scenarios
    """
    try:
        if message_type == "reset_request":
            subject, html_content = email_templates.render_reset_password(
                reset_token
            )
        elif message_type == "reset_success":
            subject, html_content = email_templates.render_reset_success()
        else:
            logger.error(f"Unknown message type: {message_type}")
            return

        if not html_content.strip():
            logger.warning("Using fallback email content")
            if message_type == "reset_request":
                subject = "Сброс пароля"
                html_content = f"""
                <html>
                <body>
                    <h2>Сброс пароля</h2>
                    <p>Для сброса пароля перейдите по ссылке:</p>
                    <a href="http://localhost:3000/reset_password?token={reset_token}">
                        Сбросить пароль
                    </a>
                    <p>Или используйте токен: {reset_token}</p>
                </body>
                </html>
                """
            else:
                subject = "Пароль успешно изменен"
                html_content = """
                <html>
                <body>
                    <h2>Пароль успешно изменен</h2>
                    <p>Ваш пароль был успешно изменен.</p>
                </body>
                </html>
                """

        success = await send_email(to_email, subject, html_content)

        crud = db_manager.get_notification_crud()
        if success:
            await crud.update_status(notification_id, "sent")
            logger.info(
                f"Email sent successfully for notification: {notification_id}"
            )
        else:
            await crud.update_status(notification_id, "failed")
            logger.error(
                f"Failed to send email for notification: {notification_id}"
            )

    except Exception as e:
        logger.error(f"Error in email sending task: {e}")
