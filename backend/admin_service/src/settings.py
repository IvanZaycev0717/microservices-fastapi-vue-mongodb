import logging
from datetime import timedelta
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ADMIN_SERVICE_HOST: str
    ADMIN_SERVICE_PORT: int

    # Secrets
    SECRET_KEY: SecretStr
    ALGORITHM: str
    ADMIN_EMAIL: SecretStr
    ADMIN_PASSWORD: SecretStr

    # CORS
    ADMIN_GUI_URL: str = "http://localhost:9500"

    # Cookie Settings
    COOKIE_KEY: str = "refresh_token"
    COOKIE_HTTPONLY: bool = True
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_PATH: str = "/"

    # MondoDB Settings
    CONTENT_ADMIN_MONGO_ROOT_USERNAME: str = Field(
        description="MongoDB root username"
    )
    CONTENT_ADMIN_MONGO_ROOT_PASSWORD: str = Field(
        description="MongoDB root password"
    )
    CONTENT_ADMIN_MONGODB_URL: str = Field(
        description="MongoDB connection URL"
    )
    CONTENT_ADMIN_MONGO_DATABASE_NAME: str = Field(
        description="MongoDB database name"
    )
    CONTENT_ADMIN_MONGO_PORT: int = Field(description="MongoDB port")
    CONTENT_ADMIN_ME_CONFIG_MONGODB_URL: str = Field(
        description="Mongo Express connection URL"
    )

    # PostgreSQL Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    COMMENTS_ADMIN_POSTGRES_ROOT_NAME: str
    COMMENTS_ADMIN_POSTGRES_PORT: int
    COMMENTS_ADMIN_POSTGRES_DB_NAME: str
    COMMENTS_ADMIN_POSTGRES_DB_URL: str
    POSTGRES_CONNECTION_TIMEOUT: int = 30
    POSTGRES_COMMAND_TIMEOUT: int = 60
    POSTGRES_POOL_MIN_SIZE: int = 1
    POSTGRES_POOL_MAX_SIZE: int = 10

    # Auth Admin
    AUTH_ADMIN_MONGO_ROOT_USERNAME: str = Field(
        description="MongoDB root username for auth database"
    )
    AUTH_ADMIN_MONGO_ROOT_PASSWORD: str = Field(
        description="MongoDB root password for auth database"
    )
    AUTH_ADMIN_MONGODB_URL: str = Field(
        description="MongoDB connection URL for auth database"
    )
    AUTH_ADMIN_MONGO_DATABASE_NAME: str = Field(
        description="MongoDB database name for auth database"
    )
    AUTH_ADMIN_MONGO_PORT: int = Field(
        description="MongoDB port for auth database"
    )
    AUTH_ADMIN_ME_CONFIG_MONGODB_URL: str = Field(
        description="Mongo Express connection URL for auth database"
    )

    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_CACHE_INVALIDATION_TOPIC: str = "cache-invalidation"
    KAFKA_LOGS_TOPIC: str = "admin_service_logs"
    KAFKA_LOGS_ENABLED: bool = True
    KAFKA_IS_IDEMPOTENCE_ENABLED: bool = True
    KAFKA_ACKS: str = "all"
    KAFKA_RETRIES: int = 3

    # Tokens Settings
    ACCESS_TOKEN_EXPIRE_AT: timedelta = timedelta(minutes=30)
    REFRESH_TOKEN_EXPIRES_AT: timedelta = timedelta(days=7)

    # Notification Admin
    NOTIFICATION_ADMIN_MONGO_ROOT_USERNAME: str = Field(
        description="MongoDB root username for notification database"
    )
    NOTIFICATION_ADMIN_MONGO_ROOT_PASSWORD: str = Field(
        description="MongoDB root password for notification database"
    )
    NOTIFICATION_ADMIN_MONGODB_URL: str = Field(
        description="MongoDB connection URL for notification database"
    )
    NOTIFICATION_ADMIN_MONGO_DATABASE_NAME: str = Field(
        description="MongoDB database name for notification database"
    )
    NOTIFICATION_ADMIN_MONGO_PORT: int = Field(
        description="MongoDB port for notification database"
    )
    NOTIFICATION_ADMIN_ME_CONFIG_MONGODB_URL: str = Field(
        description="Mongo Express connection URL for notification database"
    )

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_HOST: str = "minio"
    MINIO_API_PORT: int = 9000
    MINIO_PUBLIC_URL: str = Field(
        "http://localhost:9000",
        description="MinIO public URL for container access",
    )

    # Service Names Configurations
    SERVICE_NAME: str = "ADMIN_SERVICE"

    # Content Service Names
    CONTENT_ADMIN_ABOUT_NAME: str = "Content Admin - About"
    CONTENT_ADMIN_TECH_NAME: str = "Content Admin - Tech"
    CONTENT_ADMIN_PROJECTS_NAME: str = "Content Admin - Projects"
    CONTENT_ADMIN_CERTIFICATES_NAME: str = "Content Admin- Certificates"
    CONTENT_ADMIN_PUBLICATIONS_NAME: str = "Content Admin - Publications"

    # Auth Service Name
    AUTH_ADMIN_NAME: str = "Auth Service"

    # Comments Service Name
    COMMENTS_ADMIN_NAME: str = "Comments Service"

    # Notifications Service Name
    NOTIFICATION_ADMIN_NAME: str = "Notifications Service"

    # Comments Service Settings
    COMMENTS_PROJECT_ID_LENGTH: int = 24
    COMMENTS_AUTHOR_ID_LENGTH: int = 24
    MIN_COMMENT_LENGTH: int = 1
    MAX_COMMENT_LENGTH: int = 1000

    # Image Directories Names
    ABOUT_BUCKET_NAME: str = "about"
    PROJECTS_BUCKET_NAME: str = "projects"
    CERTIFICATES_BUCKET_NAME: str = "certificates"

    # Paths configuration
    CONTENT_ADMIN_PATH: Path = Path("content_admin/data")
    IMAGE_STORAGE_PATH: Path = Path("static/images")
    ABOUT_IMAGES_PATH: Path = IMAGE_STORAGE_PATH / ABOUT_BUCKET_NAME

    # Initial Data Loading Files
    INITIAL_DATA_LOADING_FILES: set[str] = {
        "about.json",
        "certificates.json",
        "projects.json",
        "publications.json",
        "tech.json",
        "image1.webp",
        "image2.webp",
    }

    # Image validation settings
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {
        ".png",
        ".webp",
        ".jpg",
        ".jpeg",
        ".avif",
        ".gif",
    }
    ABOUT_MAX_IMAGE_SIZE_KB: int = 500 * 1024  # 500KB
    PROJECT_MAX_IMAGE_SIZE_KB: int = 12_000 * 1024  # 12MB
    CERTIFICATE_MAX_IMAGE_SIZE_KB: int = 1024 * 1024  # 1MB
    CERTIFICATE_MAX_PDF_SIZE_KB: int = 5_000 * 1024  # 5MB

    # Forms Validation Settings
    MIN_TITLE_LENGTH: int = 1
    MAX_TITLE_LENGTH: int = 63
    MAX_DESCRIPTION_LENGTH: int = 255
    MIN_HTML_IMAGE_ALT_LENGTH: int = 1
    MAX_HTML_IMAGE_ALT_LENGTH: int = 255
    MIN_POPULARITY_BOUNDARY: int = 0
    MAX_POPULARITY_BOUNDARY: int = 1000
    MIN_PUBLICATIONS_RATING_BOUNDARY: int = -1000
    MAX_PUBLICATIONS_RATING_BOUNDARY: int = 1000
    MIN_PASSWORD_LENGTH: int = 5
    MAX_PASSWORD_LENGTH: int = 31
    MIN_EMAIL_LENGTH: int = 3
    MAX_EMAIL_LENGTH: int = 255

    # About Images Sizes PIXELS
    ABOUT_IMAGE_OUTPUT_WIDTH: int = 1024
    ABOUT_IMAGE_OUTPUT_HEIGHT: int = 1024

    # Projects Images Sizes
    PROJECTS_IMAGE_THUMB_OUTPUT_WIDTH: int = 300
    PROJECTS_IMAGE_THUMB_OUTPUT_HEIGHT: int = 169

    # Certificates Images Sizes
    CERTIFICATES_IMAGE_OUTPUT_WIDTH: int = 594
    CERTIFICATES_IMAGE_OUTPUT_HEIGHT: int = 841
    CERTIFICATES_IMAGE_THUMB_OUTPUT_WIDTH: int = 206
    CERTIFICATES_IMAGE_THUMB_OUTPUT_HEIGHT: int = 300

    # MongoDB connection settings
    MONGO_DB_CONNECTION_TIMEOUT_MS: int = Field(
        3000, description="MongoDB connection timeout in milliseconds"
    )
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = Field(
        3000, description="MongoDB server selection timeout in milliseconds"
    )

    # MongoDB Objects Validation
    MONGO_ID_VALID_ID_REGEXP: str = r"^[0-9a-fA-F]{24}$"

    # Logging configuration
    LOGGING_LEVEL: int = Field(logging.INFO, description="Logging level")

    # PDF Settings
    PDF_FIRST_PAGE: int = 1
    PDF_LAST_PAGE: int = 1
    PDF_DPI: int = 300
    PDF_OUTPUT_IMAGE_FORMAT: str = "webp"
    PDF_THREAD_COUNT: int = 4

    # Email Settings
    IS_SEND_EMAIL_ENABLED: bool = True
    SMTP_USERNAME: SecretStr
    SMTP_PASSWORD: SecretStr
    SMTP_FROM: SecretStr
    SMTP_SERVER: str = "smtp.yandex.ru"
    SMTP_PORT: int = 465

    MIN_EMAIL_SUBJECT_LENGHT: int = 1
    MAX_EMAIL_SUBJECT_LENGHT: int = 63
    MIN_EMAIL_MESSAGE_LENGTH: int = 1
    MAX_EMAIL_MESSAGE_LENGHT: int = 255

    def create_directories(self):
        """Create necessary directories on startup"""
        self.ABOUT_IMAGES_PATH.mkdir(parents=True, exist_ok=True)

    @property
    def PATH_ABOUT_JSON(self) -> Path:
        """Path to about.json data file."""
        return self.CONTENT_ADMIN_PATH / "about.json"

    @property
    def PATH_TECH_JSON(self) -> Path:
        """Path to tech.json data file."""
        return self.CONTENT_ADMIN_PATH / "tech.json"

    @property
    def PATH_PROJECTS_JSON(self) -> Path:
        """Path to projects.json data file."""
        return self.CONTENT_ADMIN_PATH / "projects.json"

    @property
    def PATH_CERTIFICATES_JSON(self) -> Path:
        """Path to certificates.json data file."""
        return self.CONTENT_ADMIN_PATH / "certificates.json"

    @property
    def PATH_PUBLICATIONS_JSON(self) -> Path:
        """Path to publications.json data file."""
        return self.CONTENT_ADMIN_PATH / "publications.json"


settings = Settings()
