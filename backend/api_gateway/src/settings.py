from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Gateway
    API_GATEWAY_NAME: str
    API_GATEWAY_HOST: str
    API_GATEWAY_PORT: int

    # Auth Service
    GRPC_AUTH_HOST: str
    GRPC_AUTH_PORT: int

    # Content Service
    GRPC_CONTENT_HOST: str
    GRPC_CONTENT_PORT: int

    # Comments Service
    GRPC_COMMENTS_HOST: str
    GRPC_COMMENTS_PORT: int

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


settings = Settings()
