import logging
from enum import StrEnum
from typing import Callable

from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from content_admin.crud.about import AboutCRUD
from content_admin.crud.certificates import CertificatesCRUD
from content_admin.crud.projects import ProjectsCRUD
from content_admin.crud.publications import PublicationsCRUD
from content_admin.crud.tech import TechCRUD
from services.logger import get_logger
from services.minio_management import MinioCRUD


class Language(StrEnum):
    EACH = "Each lang"
    EN = "en"
    RU = "ru"


class SortOrder(StrEnum):
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    POPULARITY = "popularity"





def get_logger_dependency() -> logging.Logger:
    """Get configured logger instance for dependency injection.

    Returns:
        logging.Logger: Pre-configured logger instance.
    """
    return get_logger()


def get_logger_factory(name: str) -> Callable[[], logging.Logger]:
    """Factory function that returns a callable to inject named logger into dependencies."""

    def inner():
        return get_logger(name=name)

    return inner


def get_minio_crud() -> MinioCRUD:
    """Get MinIO CRUD manager instance for dependency injection.

    Returns:
        MinioCRUD: Initialized MinIO CRUD operations manager.
    """
    return MinioCRUD()


async def get_db(request: Request) -> AsyncDatabase:
    """Get MongoDB database connection from application state.

    Args:
        request: FastAPI request object containing application state.

    Returns:
        AsyncDatabase: Asynchronous MongoDB database connection.
    """
    return request.app.state.content_admin_mongo_db


async def get_about_crud(db: AsyncDatabase = Depends(get_db)) -> AboutCRUD:
    """Get AboutCRUD instance with database dependency.

    Args:
        db: AsyncDatabase connection injected as dependency.

    Returns:
        AboutCRUD: Initialized About content CRUD operations manager.
    """
    return AboutCRUD(db)


async def get_tech_crud(db: AsyncDatabase = Depends(get_db)) -> TechCRUD:
    """Get TechCRUD instance with database dependency.

    Args:
        db: AsyncDatabase connection injected as dependency.

    Returns:
        TechCRUD: Initialized Tech content CRUD operations manager.
    """
    return TechCRUD(db)


async def get_projects_crud(
    db: AsyncDatabase = Depends(get_db),
) -> ProjectsCRUD:
    return ProjectsCRUD(db)


async def get_certificates_crud(
    db: AsyncDatabase = Depends(get_db),
) -> CertificatesCRUD:
    return CertificatesCRUD(db)


async def get_publications_crud(
    db: AsyncDatabase = Depends(get_db),
) -> PublicationsCRUD:
    return PublicationsCRUD(db)
