from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    CONTENT_SERVICE_NAME: str

    # MongoDB connection settings
    MONGO_CONNECTION_TIMEOUT_MS: int
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int

    # gRPC Server
    GRPC_HOST: str
    GRPC_PORT: int

    # Logging
    LOG_LEVEL: str

    # Validation boundaries
    MIN_TITLE_LENGTH: int
    MAX_TITLE_LENGTH: int
    MAX_DESCRIPTION_LENGTH: int

    MIN_POPULARITY_BOUNDARY: int
    MAX_POPULARITY_BOUNDARY: int

    MIN_PUBLICATIONS_RATING_BOUNDARY: int
    MAX_PUBLICATIONS_RATING_BOUNDARY: int


settings = Settings()
