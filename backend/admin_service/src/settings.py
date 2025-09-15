import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # From .env file

    # Content Admin
    CONTENT_ADMIN_MONGO_ROOT_USERNAME: str = Field(description="MongoDB root username")
    CONTENT_ADMIN_MONGO_ROOT_PASSWORD: str = Field(description="MongoDB root password")
    CONTENT_ADMIN_MONGODB_URL: str = Field(description="MongoDB connection URL")
    CONTENT_ADMIN_MONGO_DATABASE_NAME: str = Field(description="MongoDB database name")
    CONTENT_ADMIN_MONGO_PORT: int = Field(description="MongoDB port")
    CONTENT_ADMIN_ME_CONFIG_MONGODB_URL: str = Field(
        description="Mongo Express connection URL"
    )

    # Object Storage
    MINIO_ROOT_USER: str = Field(description="MinIO user name")
    MINIO_ROOT_PASSWORD: str = Field(description="MinIO password")
    MINIO_HOST: str = Field(description="MinIO host")
    MINIO_PORT: str = Field(description="MinIO port")

    # Service configuration
    SERVICE_NAME: str = "ADMIN_SERVICE"
    CONTENT_SERVICE_ABOUT_NAME: str = "Content Service - About"
    CONTENT_SERVICE_TECH_NAME: str = "Content Service - Tech"
    CONTENT_SERVICE_PROJECTS_NAME: str = "Content Service - Projects"
    CONTENT_SERVICE_CERTIFICATES_NAME: str = "Content Service - Certificates"

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
    CERTIFICATE_MAX_IMAGE_SIZE_KB: int = 1024 * 1024 # 1MB
    CERTIFICATE_MAX_PDF_SIZE_KB: int = 5_000 * 1024 # 5MB

    # Forms Validation Settings
    MAX_TITLE_LENGTH: int = 63
    MAX_DESCRIPTION_LENGTH: int = 255
    MIN_HTML_IMAGE_ALT_LENGTH: int = 1
    MAX_HTML_IMAGE_ALT_LENGTH: int = 255
    MIN_POPULARITY_BOUNDARY: int = 0
    MAX_POPULARITY_BOUNDARY: int = 1000

    # About Images Sizes
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

    # Logging configuration
    LOGGING_LEVEL: int = Field(logging.INFO, description="Logging level")

    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )

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
