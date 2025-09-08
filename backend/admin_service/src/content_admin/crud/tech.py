from typing import List, Dict, Any
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from services.logger import get_logger
from content_admin.models.tech import TechResponse

logger = get_logger("tech-crud")


class TechCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.tech

    async def read_all(self) -> List[TechResponse]:
        try:
            cursor = self.collection.find()
            results = await cursor.to_list(length=None)
            return [TechResponse(**doc) for doc in results]
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise

    def _format_tech_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        formatted_result = {}

        field_to_kingdom = {
            "backend": "backend_kingdom",
            "database": "database_kingdom",
            "frontend": "frontend_kingdom",
            "desktop": "desktop_kingdom",
            "devops": "devops_kingdom",
            "telegram": "telegram_kingdom",
            "parsing": "parsing_kingdom",
            "computer_science": "computerscience_kingdom",
            "game_dev": "gamedev_kingdom",
            "ai": "ai_kingdom",
        }

        for db_field, kingdom_key in field_to_kingdom.items():
            if db_field in raw_data:
                formatted_result[kingdom_key] = {
                    "kingdom": self._get_kingdom_display_name(db_field),
                    "items": raw_data[db_field],
                }
            else:
                formatted_result[kingdom_key] = {
                    "kingdom": self._get_kingdom_display_name(db_field),
                    "items": [],
                }

        return formatted_result

    def _get_kingdom_display_name(self, field_name: str) -> str:
        display_names = {
            "backend": "Backend",
            "database": "Databases",
            "frontend": "Frontend",
            "desktop": "Desktop",
            "devops": "DevOps",
            "telegram": "Telegram",
            "parsing": "Parsing",
            "computer_science": "ComputerScience",
            "game_dev": "GameDev",
            "ai": "AI",
        }
        return display_names.get(field_name, field_name.capitalize())

    def _get_empty_kingdoms_structure(self) -> Dict[str, Any]:
        return {
            "backend_kingdom": {"kingdom": "Backend", "items": []},
            "database_kingdom": {"kingdom": "Databases", "items": []},
            "frontend_kingdom": {"kingdom": "Frontend", "items": []},
            "desktop_kingdom": {"kingdom": "Desktop", "items": []},
            "devops_kingdom": {"kingdom": "DevOps", "items": []},
            "telegram_kingdom": {"kingdom": "Telegram", "items": []},
            "parsing_kingdom": {"kingdom": "Parsing", "items": []},
            "computerscience_kingdom": {"kingdom": "ComputerScience", "items": []},
            "gamedev_kingdom": {"kingdom": "GameDev", "items": []},
            "ai_kingdom": {"kingdom": "AI", "items": []},
        }

    async def update_kingdom(self, kingdom_type: str, items: List[str]) -> bool:
        """
        Обновляет items для конкретного kingdom
        
        Args:
            kingdom_type: Тип kingdom (backend, database, etc.)
            items: Список навыков
            
        Returns:
            bool: True если обновление успешно
        """
        try:
            # Проверяем, существует ли документ
            existing_doc = await self.collection.find_one({})

            if existing_doc:
                # Обновляем существующий документ
                result = await self.collection.update_one(
                    {"_id": existing_doc["_id"]},
                    {"$set": {kingdom_type: items}}
                )
            else:
                # Создаем новый документ со ВСЕМИ полями (изначально пустыми)
                new_doc = self._create_initial_document(kingdom_type, items)
                result = await self.collection.insert_one(new_doc)

            return result.acknowledged

        except Exception as e:
            logger.error(f"Database error in TechCRUD.update_kingdom: {e}")
            raise

    def _create_initial_document(self, updated_kingdom: str, items: List[str]) -> Dict[str, Any]:
        """
        Создает начальный документ со всеми полями, где одно поле заполнено
        
        Args:
            updated_kingdom: Поле которое нужно заполнить
            items: Значения для заполнения
            
        Returns:
            Dict[str, Any]: Документ со всеми полями
        """
        # Создаем документ со всеми полями (пустыми массивами)
        initial_doc = {
            "backend": [],
            "database": [],
            "frontend": [],
            "desktop": [],
            "devops": [],
            "telegram": [],
            "parsing": [],
            "computer_science": [],
            "game_dev": [],
            "ai": []
        }
        
        # Заполняем только то поле, которое пришло в запросе
        initial_doc[updated_kingdom] = items
        
        return initial_doc

    async def initialize_tech_data(self) -> None:
        """
        Инициализирует коллекцию tech начальными данными, если она пустая
        """
        try:
            existing_doc = await self.collection.find_one({})
            if not existing_doc:
                # Создаем документ со всеми полями (пустыми массивами)
                initial_doc = {
                    "backend": [],
                    "database": [],
                    "frontend": [],
                    "desktop": [],
                    "devops": [],
                    "telegram": [],
                    "parsing": [],
                    "computer_science": [],
                    "game_dev": [],
                    "ai": []
                }
                await self.collection.insert_one(initial_doc)
                logger.info("Tech collection initialized with empty structure")
                
        except Exception as e:
            logger.error(f"Failed to initialize tech collection: {e}")
            raise