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


settings = Settings()
