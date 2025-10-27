from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from comments_admin.crud import CommentsCRUD


@pytest.fixture
def mock_db_session():
    mock_session = Mock(spec=AsyncSession)

    mock_session.add = Mock()
    mock_session.flush = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.scalar = AsyncMock()

    return mock_session


@pytest.fixture
async def comments_crud(mock_db_session):
    return CommentsCRUD(mock_db_session)
