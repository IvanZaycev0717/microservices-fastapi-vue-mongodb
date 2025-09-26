import pytest
from mimesis import Generic
from mongomock_motor import AsyncMongoMockClient

from src.auth_admin.crud.auth import AuthCRUD
from src.auth_admin.crud.token import TokenCRUD


@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client.test_db
    return db


@pytest.fixture
async def auth_crud(mock_db):
    return AuthCRUD(mock_db)


@pytest.fixture
async def token_crud(mock_db):
    return TokenCRUD(mock_db)


@pytest.fixture
def fake():
    return Generic("en")
