from pymongo import AsyncMongoClient
from services.logger import get_logger
from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo.asynchronous.topology import ServerSelectionTimeoutError
import json
from pathlib import Path

from settings import (
    PATH_ABOUT_JSON,
    MONGO_DB_CONNECTION_TIMEOUT_MS,
    MONGO_SERVER_SELECTION_TIMEOUT_MS,
)

logger = get_logger("content_service_db_connection")


class MongoDB:
    def __init__(self, host: str) -> None:
        self.host = host
        self.client = None
        self.db = None

    async def open_client(self) -> None:
        try:
            self.client = AsyncMongoClient(
                self.host,
                connectTimeoutMS=MONGO_DB_CONNECTION_TIMEOUT_MS,
                serverSelectionTimeoutMS=MONGO_SERVER_SELECTION_TIMEOUT_MS,
            )
            await self.client.admin.command("ping")
            logger.info("MongoDB connection successful")
        except OperationFailure as e:
            if "Authentication failed" in str(e):
                logger.error("MongoDB authentication failed: invalid login or password")
            else:
                logger.error(f"MongoDB operation failed: {e}")

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection failed: {e}")

    async def close_client(self):
        if self.client:
            await self.client.close()

    async def check_database_existence(self, db_name: str) -> bool:
        """Проверяет существование базы данных"""
        try:
            databases = await self.client.list_database_names()

            if db_name in databases:
                logger.info(f"{db_name} exists in client")
                return True
            else:
                logger.warning(f"{db_name} doesnt exist in client")
                return False

        except OperationFailure as e:
            logger.error(f"Database check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during database check: {e}")
            return False

    async def create_database(self, db_name: str) -> bool:
        """Создает базу данных если она не существует"""
        try:
            self.db = self.client[db_name]
            await self.db.command("ping")
            logger.info(f"Database '{db_name}' created successfully")
            return True

        except OperationFailure as e:
            logger.error(f"Failed to create database: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating database: {e}")
            return False

    @staticmethod
    async def load_and_insert_data(file_path: Path, collection, logger):
        """Загружает данные из JSON и вставляет в коллекцию"""
        try:
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    await collection.insert_many(data)
                    logger.info(f"Data loaded from {file_path.name}")
            else:
                logger.warning(f"File {file_path} not found")
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")

    async def initialize_collections(self):
        """Инициализирует все коллекции с начальными данными"""
        try:
            await self.load_and_insert_data(PATH_ABOUT_JSON, self.db["about"], logger)

            # # 2. Technologies коллекция
            # skills_data = {
            #     "backend_kingdom": {
            #         "kingdom": "Backend",
            #         "items": ["Skill 1", "Skill 2"],
            #     },
            #     "database_kingdom": {
            #         "kingdom": "Databases",
            #         "items": ["Skill 1", "Skill 2"],
            #     },
            #     "language": "en",
            # }
            # await self.db.technologies.insert_one(skills_data)

            # # 3. Projects коллекция
            # projects_data = [
            #     {
            #         "id": 1,
            #         "title": "Project 1",
            #         "thumbnail": "image1Thumb",
            #         "image": "image1",
            #         "description": "Project 1",
            #         "link": "https://example.com",
            #         "date": datetime.datetime(2025, 3, 14),
            #         "popularity": 2,
            #         "language": "en",
            #     },
            #     # ... остальные проекты
            # ]
            # await self.db.projects.insert_many(projects_data)

            # # 4. Certificates коллекция
            # certificates_data = [
            #     {
            #         "src": "MinDigitalCom_ALGOR",
            #         "thumb": "MinDigitalCom_ALGORThumb",
            #         "date": datetime.datetime(2025, 7, 13),
            #         "popularity": 85,
            #         "alt": "MinDigitalCom_ALGOR",
            #         "language": "en",
            #     },
            #     # ... остальные сертификаты
            # ]
            # await self.db.certificates.insert_many(certificates_data)

            # # 5. Publications коллекция
            # publications_data = [
            #     {
            #         "id": 1,
            #         "title": "Some random text",
            #         "page": "https://example.com",
            #         "site": "https://example.com",
            #         "rating": 18,
            #         "date": "08.08.2025",
            #         "language": "en",
            #     }
            # ]
            # await self.db.publications.insert_many(publications_data)

            logger.info("All collections initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
