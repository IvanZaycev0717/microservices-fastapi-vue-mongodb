from pathlib import Path

from logger import get_logger
from settings import settings

logger = get_logger(f"{settings.NOTIFICATION_SERVICE_NAME} - EmailTemplates")


class EmailTemplateManager:
    """Manager for loading and rendering email templates."""

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.css_file = self.templates_dir / "css" / "email_styles.css"
        self._css_content = None

    def _load_css(self) -> str:
        """Load CSS styles from file."""
        if self._css_content is None:
            try:
                with open(self.css_file, "r", encoding="utf-8") as f:
                    self._css_content = f.read()
            except Exception as e:
                logger.error(f"Failed to load CSS: {e}")
                self._css_content = ""
        return self._css_content

    def _load_template(self, template_name: str) -> str:
        """Load HTML template from file."""
        try:
            template_path = self.templates_dir / "emails" / template_name
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return ""

    def render_reset_password(self, reset_token: str) -> tuple[str, str]:
        """Render password reset email template.

        Args:
            reset_token: Password reset token

        Returns:
            tuple: (subject, html_content)
        """
        subject = "🔐 Сброс пароля"
        template = self._load_template("reset_password.html")
        css_content = self._load_css()

        html_content = template.replace("{{ css_content }}", css_content)
        html_content = html_content.replace("{{ reset_token }}", reset_token)

        return subject, html_content

    def render_reset_success(self) -> tuple[str, str]:
        """Render password reset success email template.

        Returns:
            tuple: (subject, html_content)
        """
        subject = "✅ Пароль успешно изменен"
        template = self._load_template("successful_reset.html")
        css_content = self._load_css()

        html_content = template.replace("{{ css_content }}", css_content)

        return subject, html_content


email_templates = EmailTemplateManager()