import pytest
from mimesis import Generic
from mongomock_motor import AsyncMongoMockClient

from src.content_admin.crud.about import AboutCRUD


@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client.test_db
    return db


@pytest.fixture
async def about_crud(mock_db):
    return AboutCRUD(mock_db)


@pytest.fixture
def fake():
    return Generic("en")
