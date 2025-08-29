from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, List

from services.logger import get_logger


logger = get_logger('content_service_database')


class MongoDB:
    def __init__(self, mongodb_url: str, database_name: Optional[str] = None) -> None:
        self.mongodb_url = mongodb_url
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.is_connected: bool = False

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(self.mongodb_url)
            await self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {self.client}")
            if self.database_name:
                await self._handle_database()
            self.is_connected = True
            return self.client
        except AttributeError as e:
            logger.exception(f'MongoDB URL is wrong - {e}')
        except ValueError as e:
            logger.exception(e)


    async def _handle_database(self) -> None:
        if not self.database_name:
            raise ValueError("Database name is not specified")
        is_database_exist = await self.is_database_exist()
        if not is_database_exist:
            logger.info(f"Database '{self.database_name}' doesn't exist, creating...")
            await self.create_database()
        else:
            self.database = self.client[self.database_name]
            logger.info(f"Database '{self.database_name}' already exists")


    async def is_database_exist(self) -> bool:
        try:
            database_names = await self.client.list_database_names()
            return self.database_name in database_names
        except Exception as e:
            logger.error(f"Error checking database existence: {e}")
            return False
    
    async def create_database(self):
        logger.info('Need to create database')