from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # MongoDB
    GRPC_AUTH_MONGODB_URL: SecretStr
    GRPC_AUTH_MONGODB_DB_NAME: str

    # Service
    GRPC_AUTH_NAME: str

    # gRPC Server
    GRPC_AUTH_GRPC_HOST: str
    GRPC_AUTH_PORT: int

    # Logging
    LOG_LEVEL: str

    # MongoDB Connection Timeouts
    MONGO_CONNECTION_TIMEOUT_MS: int
    MONGO_SERVER_SELECTION_TIMEOUT_MS: int

    # Secrets
    SECRET_KEY: SecretStr
    ALGORITHM: str

    # Password Constraints
    MIN_PASSWORD_LENGTH: int
    MAX_PASSWORD_LENGTH: int
    MIN_EMAIL_LENGTH: int
    MAX_EMAIL_LENGTH: int

    # Token Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int


settings = Settings()