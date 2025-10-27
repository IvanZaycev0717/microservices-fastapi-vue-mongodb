import pytest
from mimesis import Generic
from mongomock_motor import AsyncMongoMockClient

from content_admin.crud.about import AboutCRUD
from content_admin.crud.certificates import CertificatesCRUD
from content_admin.crud.projects import ProjectsCRUD
from content_admin.crud.publications import PublicationsCRUD
from content_admin.crud.tech import TechCRUD


@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client.test_db
    return db


@pytest.fixture
async def about_crud(mock_db):
    return AboutCRUD(mock_db)


@pytest.fixture
async def certificates_crud(mock_db):
    return CertificatesCRUD(mock_db)


@pytest.fixture
async def projects_crud(mock_db):
    return ProjectsCRUD(mock_db)


@pytest.fixture
async def publications_crud(mock_db):
    return PublicationsCRUD(mock_db)


@pytest.fixture
async def tech_crud(mock_db):
    return TechCRUD(mock_db)


@pytest.fixture
def fake():
    return Generic("en")
