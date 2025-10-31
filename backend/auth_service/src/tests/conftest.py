import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

from services.database import db_manager

os.environ.update(
    {
        "GRPC_AUTH_MONGODB_URL": "mongodb://test:test@localhost:27017/test",
        "GRPC_AUTH_MONGODB_DB_NAME": "test",
        "GRPC_AUTH_GRPC_HOST": "0.0.0.0",
        "GRPC_AUTH_PORT": "50052",
        "GRPC_AUTH_NAME": "Test Auth Service",
        "LOG_LEVEL": "INFO",
        "MONGO_CONNECTION_TIMEOUT_MS": "3000",
        "MONGO_SERVER_SELECTION_TIMEOUT_MS": "3000",
        "SECRET_KEY": "test-secret-key",
        "ALGORITHM": "HS256",
        "MIN_PASSWORD_LENGTH": "5",
        "MAX_PASSWORD_LENGTH": "31",
        "MIN_EMAIL_LENGTH": "3",
        "MAX_EMAIL_LENGTH": "255",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",
        "RESET_PASSWORD_TOKEN_EXPIRE_MINUTES": "15",
        "KAFKA_BOOTSTRAP_SERVERS": "broker-1:19092,broker-2:19092,broker-3:19092",
        "KAFKA_PASSWORD_RESET_TOPIC": "password-reset-requests",
    }
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def mock_database():
    with patch("services.database.AsyncMongoClient") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        db_manager.client = mock_client.return_value
        db_manager.db = mock_db
        yield
