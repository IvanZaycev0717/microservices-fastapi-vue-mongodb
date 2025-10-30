import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest

from service.database import db_manager

os.environ.update(
    {
        "MONGODB_URL": "mongodb://test:test@localhost:27017/test",
        "MONGODB_DB_NAME": "test",
        "GRPC_HOST": "0.0.0.0",
        "GRPC_PORT": "50051",
        "LOG_LEVEL": "INFO",
        "CONTENT_SERVICE_NAME": "Test Service",
        "MIN_TITLE_LENGTH": "1",
        "MAX_TITLE_LENGTH": "63",
        "MAX_DESCRIPTION_LENGTH": "255",
        "MIN_POPULARITY_BOUNDARY": "0",
        "MAX_POPULARITY_BOUNDARY": "1000",
        "MIN_PUBLICATIONS_RATING_BOUNDARY": "-1000",
        "MAX_PUBLICATIONS_RATING_BOUNDARY": "1000",
        "MONGO_CONNECTION_TIMEOUT_MS": "3000",
        "MONGO_SERVER_SELECTION_TIMEOUT_MS": "3000",
    }
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def mock_database():
    with patch("service.database.AsyncMongoClient") as mock_client:
        mock_db = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        db_manager.client = mock_client.return_value
        db_manager.db = mock_db
        yield
