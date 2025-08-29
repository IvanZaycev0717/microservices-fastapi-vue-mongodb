from database import mongodb
from logger import get_logger

logger = get_logger("content_service_init_db")


async def initialize_database():
    """Инициализация базы данных: проверка и создание коллекций при необходимости"""
    try:
        db = mongodb.get_database()

        existing_collections = await db.list_collection_names()
        logger.info(f"Existing collections: {existing_collections}")

        required_collections = ["about", "technologies", "projects"]

        for collection_name in required_collections:
            if collection_name not in existing_collections:
                await db.create_collection(collection_name)
                logger.info(f"Collection '{collection_name}' created")

        logger.info("Database initialization completed")

    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
