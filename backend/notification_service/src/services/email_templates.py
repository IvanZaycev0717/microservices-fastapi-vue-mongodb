from pathlib import Path

from settings import settings
from logger import get_logger

logger = get_logger("EmailTemplates")


class EmailTemplateManager:
    """Manages email template loading and styling.

    Handles the loading of HTML email templates and associated CSS styles
    for consistent email formatting.

    Attributes:
        templates_dir: Path to the templates directory.
        css_file: Path to the CSS styles file for emails.
        _css_content: Cached CSS content for performance.
    """

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.css_file = self.templates_dir / "css" / "email_styles.css"
        self._css_content = None

    def _load_css(self) -> str:
        """Load CSS styles from file.

        Reads CSS content from file and caches it for subsequent calls.

        Returns:
            str: CSS content as string, or empty string if loading fails.

        Note:
            - Caches CSS content to avoid repeated file reads
            - Returns empty string if file cannot be read
            - Logs errors but doesn't raise exceptions
        """
        if self._css_content is None:
            try:
                with open(self.css_file, "r", encoding="utf-8") as f:
                    self._css_content = f.read()
            except Exception as e:
                logger.error(f"Failed to load CSS: {e}")
                self._css_content = ""
        return self._css_content

    def _load_template(self, template_name: str) -> str:
        """Load HTML template from file.

        Args:
            template_name: Name of the template file to load.

        Returns:
            str: Template content as string, or empty string if loading fails.

        Note:
            - Looks for templates in 'emails' subdirectory
            - Returns empty string if template cannot be read
            - Logs errors but doesn't raise exceptions
        """
        try:
            template_path = self.templates_dir / "emails" / template_name
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return ""

    def render_reset_password(self, reset_token: str) -> tuple[str, str]:
        """Renders password reset email template.

        Args:
            reset_token: Password reset token to include in the email.

        Returns:
            tuple[str, str]: Tuple containing email subject and HTML content.

        Note:
            - Uses reset_password.html template
            - Injects CSS styles and reset token into template
            - Returns formatted subject line with emoji
        """
        subject = "🔐 Сброс пароля"
        template = self._load_template("reset_password.html")
        css_content = self._load_css()

        html_content = template.replace("{{ css_content }}", css_content)
        html_content = html_content.replace("{{ reset_token }}", reset_token)
        html_content = html_content.replace("{{ frontend_url }}", settings.FRONTEND_URL)

        return subject, html_content

    def render_reset_success(self) -> tuple[str, str]:
        """Renders password reset success email template.

        Returns:
            tuple[str, str]: Tuple containing email subject and HTML content.

        Note:
            - Uses successful_reset.html template
            - Injects CSS styles into template
            - Returns formatted subject line with emoji
        """
        subject = "✅ Пароль успешно изменен"
        template = self._load_template("successful_reset.html")
        css_content = self._load_css()

        html_content = template.replace("{{ css_content }}", css_content)

        return subject, html_content


email_templates = EmailTemplateManager()
