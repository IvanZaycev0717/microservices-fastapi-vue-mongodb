import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from logger import get_logger
from services.database import db_manager
from services.email_templates import email_templates
from settings import settings

logger = get_logger(f"{settings.NOTIFICATION_SERVICE_NAME} - EmailSending")


async def send_email(to_email: str, subject: str, html_message: str) -> bool:
    """Send HTML email using SMTP directly.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_message: HTML email content

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM.get_secret_value()
        msg['To'] = to_email
        msg['Subject'] = subject

        # Add HTML body
        msg.attach(MIMEText(html_message, 'html'))

        # Send email using SMTP
        success = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: _send_sync_email(msg, to_email)
        )
        return success

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def _send_sync_email(msg: MIMEMultipart, to_email: str) -> bool:
    """Synchronous email sending using SMTP."""
    try:
        # Create SMTP session
        server = smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT)
        
        # Login to SMTP server
        server.login(
            settings.SMTP_USERNAME.get_secret_value(),
            settings.SMTP_PASSWORD.get_secret_value()
        )
        
        # Send email
        text = msg.as_string()
        server.sendmail(
            settings.SMTP_FROM.get_secret_value(),
            to_email,
            text
        )
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"SMTP error sending to {to_email}: {e}")
        return False


async def send_notification_email(notification_id: str, to_email: str, message_type: str, reset_token: str = None):
    """Send email and update notification status.

    Args:
        notification_id: ID of the notification to update
        to_email: Recipient email address
        message_type: Type of notification (reset_request/reset_success)
        reset_token: Password reset token (only for reset_request)
    """
    try:
        # Generate HTML email from template
        if message_type == "reset_request":
            subject, html_content = email_templates.render_reset_password(reset_token)
        elif message_type == "reset_success":
            subject, html_content = email_templates.render_reset_success()
        else:
            logger.error(f"Unknown message type: {message_type}")
            return

        # Fallback if templates failed to load
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

        # Send email
        success = await send_email(to_email, subject, html_content)
        
        # Update status in database
        crud = db_manager.get_notification_crud()
        if success:
            await crud.update_status(notification_id, "sent")
            logger.info(f"Email sent successfully for notification: {notification_id}")
        else:
            await crud.update_status(notification_id, "failed")
            logger.error(f"Failed to send email for notification: {notification_id}")
            
    except Exception as e:
        logger.error(f"Error in email sending task: {e}")