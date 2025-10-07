from unittest.mock import AsyncMock

from service.database import db_manager


class TestDatabase:
    """Test database operations with mocked MongoDB."""

    async def test_get_about(self):
        mock_data = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "image_url": "test.jpg",
                "translations": {
                    "en": {"title": "Test", "description": "Test desc"}
                },
            }
        ]

        db_manager.db.about.find.return_value.to_list = AsyncMock(
            return_value=mock_data
        )

        result = await db_manager.get_about()
        assert len(result) == 1
        assert result[0].id == "507f1f77bcf86cd799439011"

    async def test_get_about_with_lang(self):
        mock_data = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "image_url": "test.jpg",
                "translations": {
                    "en": {"title": "Test", "description": "Test desc"}
                },
            }
        ]

        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_data)
        db_manager.db.about.aggregate = AsyncMock(return_value=mock_cursor)

        result = await db_manager.get_about(lang="en")
        assert len(result) == 1

    async def test_get_tech(self):
        mock_data = [
            {
                "_id": "507f1f77bcf86cd799439012",
                "backend_kingdom": {
                    "kingdom": "Backend",
                    "items": ["Python", "FastAPI"],
                },
                "database_kingdom": {
                    "kingdom": "Database",
                    "items": ["MongoDB", "PostgreSQL"],
                },
                "frontend_kingdom": {
                    "kingdom": "Frontend",
                    "items": ["Vue", "TypeScript"],
                },
                "desktop_kingdom": {"kingdom": "Desktop", "items": []},
                "devops_kingdom": {
                    "kingdom": "DevOps",
                    "items": ["Docker", "K8s"],
                },
                "telegram_kingdom": {"kingdom": "Telegram", "items": []},
                "parsing_kingdom": {"kingdom": "Parsing", "items": []},
                "computerscience_kingdom": {
                    "kingdom": "CS",
                    "items": ["Algorithms"],
                },
                "gamedev_kingdom": {"kingdom": "GameDev", "items": []},
                "ai_kingdom": {"kingdom": "AI", "items": []},
            }
        ]

        db_manager.db.tech.find.return_value.to_list = AsyncMock(
            return_value=mock_data
        )

        result = await db_manager.get_tech()
        assert len(result) == 1
        assert result[0].backend_kingdom.kingdom == "Backend"

    async def test_get_projects(self):
        mock_data = [
            {
                "_id": "507f1f77bcf86cd799439013",
                "title": {"en": "Project", "ru": "Проект"},
                "description": {"en": "Desc", "ru": "Описание"},
                "thumbnail": "thumb.jpg",
                "image": "image.jpg",
                "link": "https://example.com",
                "date": "2024-01-01T00:00:00",
                "popularity": 5,
            }
        ]

        db_manager.db.projects.find.return_value.sort.return_value.to_list = (
            AsyncMock(return_value=mock_data)
        )

        result = await db_manager.get_projects(lang="en")
        assert len(result) == 1
        assert result[0]["title"] == "Project"

    async def test_get_certificates(self):
        mock_data = [
            {
                "_id": "507f1f77bcf86cd799439014",
                "src": "cert.jpg",
                "thumb": "thumb.jpg",
                "alt": "Certificate",
                "date": "2024-01-01T00:00:00",
                "popularity": 10,
            }
        ]

        db_manager.db.certificates.find.return_value.sort.return_value.to_list = AsyncMock(
            return_value=mock_data
        )

        result = await db_manager.get_certificates()
        assert len(result) == 1
        assert result[0].id == "507f1f77bcf86cd799439014"

    async def test_get_publications(self):
        mock_data = [
            {
                "_id": "507f1f77bcf86cd799439015",
                "title": {"en": "Publication", "ru": "Публикация"},
                "page": "https://example.com/page",
                "site": "https://example.com",
                "rating": 100,
                "date": "2024-01-01T00:00:00",
            }
        ]

        db_manager.db.publications.find.return_value.sort.return_value.to_list = AsyncMock(
            return_value=mock_data
        )

        result = await db_manager.get_publications(lang="en")
        assert len(result) == 1
        assert result[0].title == "Publication"
