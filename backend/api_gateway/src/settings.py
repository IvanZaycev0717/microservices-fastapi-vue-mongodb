from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Gateway
    API_GATEWAY_NAME: str
    API_GATEWAY_HOST: str
    API_GATEWAY_PORT: int

    # Service Hosts
    API_GATEWAY_CONTENT_HOST: str
    API_GATEWAY_AUTH_HOST: str
    API_GATEWAY_COMMENTS_HOST: str

    # Service Ports
    GRPC_CONTENT_PORT: int
    GRPC_AUTH_PORT: int
    GRPC_COMMENTS_PORT: int

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    LOG_LEVEL: str

    # Cookie Settings
    COOKIE_KEY: str = "refresh_token"
    COOKIE_HTTPONLY: bool = True
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_PATH: str = "/"

    # Caching Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DB: int = 0
    CACHE_TTL_MINUTES: int = 60  # 1 hour


settings = Settings()
