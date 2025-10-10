from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GRPC_COMMENTS_POSTGRES_URL: SecretStr
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr

    GRPC_COMMENTS_SERVICE_NAME: str

    GRPC_COMMENTS_HOST: str
    GRPC_COMMENTS_PORT: int

    LOG_LEVEL: str

    POSTGRES_CONNECTION_TIMEOUT: int = 30
    POSTGRES_COMMAND_TIMEOUT: int = 60
    POSTGRES_POOL_MIN_SIZE: int = 1
    POSTGRES_POOL_MAX_SIZE: int = 10

    COMMENTS_PROJECT_ID_LENGTH: int
    COMMENTS_AUTHOR_ID_LENGTH: int
    MIN_COMMENT_LENGTH: int
    MAX_COMMENT_LENGTH: int

    MAX_EMAIL_LENGTH: int

    MONGO_ID_VALID_ID_REGEXP: str = r"^[0-9a-fA-F]{24}$"


settings = Settings()
