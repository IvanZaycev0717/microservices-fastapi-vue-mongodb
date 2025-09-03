import logging

from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from services.crud.about import AboutCRUD
from services.logger import get_logger


def get_logger_dependency() -> logging.Logger:
    return get_logger()


async def get_db(request: Request) -> AsyncDatabase:
    return request.app.state.mongo_db


async def get_about_crud(db: AsyncDatabase = Depends(get_db)) -> AboutCRUD:
    return AboutCRUD(db)
