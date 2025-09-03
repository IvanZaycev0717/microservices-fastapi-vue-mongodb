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
    SERVICE_NAME: str = Field("CONTENT_SERVICE_ADMIN", description="Service identifier name")

    # Paths configuration
    DATA_PATH: Path = Field(Path("data"), description="Base path for data files")

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
