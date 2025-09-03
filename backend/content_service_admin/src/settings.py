import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # From .env file
    MONGO_ROOT_USERNAME: str = Field(description="MongoDB root username")
    MONGO_ROOT_PASSWORD: str = Field(description="MongoDB root password")
    MONGODB_URL: str = Field(description="MongoDB connection URL")
    MONGO_DATABASE: str = Field(description="MongoDB database name")
    MONGO_PORT: int = Field(description="MongoDB port")
    ME_CONFIG_MONGODB_URL: str = Field(description="Mongo Express connection URL")

    # Service configuration
    SERVICE_NAME: str = Field(
        "CONTENT_SERVICE_ADMIN", description="Service identifier name"
    )

    # Paths configuration
    DATA_PATH: Path = Field(Path("data"), description="Base path for data files")
    IMAGE_STORAGE_PATH: Path = Path("static/images")
    ABOUT_STR: str = "about"
    ABOUT_IMAGES_PATH: Path = IMAGE_STORAGE_PATH / ABOUT_STR

    # Image validation settings
    ALLOWED_IMAGE_EXTENSIONS: set[str] = {".png", ".webp", ".jpg", ".jpeg", ".avif"}
    MAX_IMAGE_SIZE_KB: int = 500
    IMAGE_OUTPUT_WIDTH: int = 1024
    IMAGE_OUTPUT_HEIGHT: int = 1024

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
        return self.DATA_PATH / "about.json"

    @property
    def PATH_TECH_JSON(self) -> Path:
        """Path to tech.json data file."""
        return self.DATA_PATH / "tech.json"

    @property
    def PATH_PROJECTS_JSON(self) -> Path:
        """Path to projects.json data file."""
        return self.DATA_PATH / "projects.json"

    @property
    def PATH_CERTIFICATES_JSON(self) -> Path:
        """Path to certificates.json data file."""
        return self.DATA_PATH / "certificates.json"

    @property
    def PATH_PUBLICATIONS_JSON(self) -> Path:
        """Path to publications.json data file."""
        return self.DATA_PATH / "publications.json"

    @property
    def MONGO_DB_NAME(self) -> str:
        """MongoDB database name (alias for MONGO_DATABASE)."""
        return self.MONGO_DATABASE


settings = Settings()
