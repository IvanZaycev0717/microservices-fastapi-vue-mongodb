import pytest
from mimesis import Generic
from mongomock_motor import AsyncMongoMockClient

from src.notification_admin.crud.notification import NotificationCRUD


@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client.test_db
    return db


@pytest.fixture
async def notification_crud(mock_db):
    return NotificationCRUD(mock_db)


@pytest.fixture
def fake():
    return Generic("en")