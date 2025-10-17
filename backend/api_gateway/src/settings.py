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

    # Logging
    LOG_LEVEL: str

    # Cookie Settings
    COOKIE_KEY: str = "refresh_token"
    COOKIE_HTTPONLY: bool = True
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_PATH: str = "/"

    # Redis Settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # Cache Settings
    REDIS_CACHE_DB: int = 0
    REDIS_RATE_LIMIT_DB: int = 1
    CACHE_TTL_MINUTES: int = 60

    # Rate Limiter Settings
    RATE_LIMIT_CAPACITY: int = 100
    RATE_LIMIT_REFILL_RATE: float = 100.0 / 3600
    AUTH_RATE_LIMIT_CAPACITY: int = 10
    AUTH_RATE_LIMIT_REFILL_RATE: float = 10.0 / 3600
    COMMENTS_RATE_LIMIT_CAPACITY: int = 30
    COMMENTS_RATE_LIMIT_REFILL_RATE: float = 30.0 / 3600
    CACHE_TTL_MINUTES: int = 30

    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_CACHE_INVALIDATION_TOPIC: str
    KAFKA_CONSUMER_GROUP_ID: str
    KAFKA_AUTO_OFFSET_RESET: str
    KAFKA_ENABLE_AUTO_COMMIT: bool = True


settings = Settings()
