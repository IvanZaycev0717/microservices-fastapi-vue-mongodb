from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    CONTENT_SERVICE_NAME: str = 'Content Service'

    # MongoDB connection settings
    MONGO_CONNECTION_TIMEOUT_MS: int = 3000
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int = 3000

    # gRPC Server
    GRPC_HOST: str
    GRPC_PORT: int

    # Logging
    LOG_LEVEL: str

    # Validation boundaries
    MIN_TITLE_LENGTH: int = 1
    MAX_TITLE_LENGTH: int = 255
    MAX_DESCRIPTION_LENGTH: int = 255

    MIN_POPULARITY_BOUNDARY: int = 0
    MAX_POPULARITY_BOUNDARY: int = 1000

    MIN_PUBLICATIONS_RATING_BOUNDARY: int = -1000
    MAX_PUBLICATIONS_RATING_BOUNDARY: int = 1000

    model_config = SettingsConfigDict(
        env_file="../.env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
