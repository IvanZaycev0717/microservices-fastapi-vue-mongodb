from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str

    # gRPC Server
    GRPC_HOST: str
    GRPC_PORT: int

    # Logging
    LOG_LEVEL: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
