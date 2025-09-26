from datetime import datetime
from bson import ObjectId


class TestProjectsCRUD:
    async def test_create_project(self, projects_crud, fake):
        test_data = {
            "title": {"en": "English Title", "ru": "Русский заголовок"},
            "thumbnail": fake.internet.uri(),
            "image": fake.internet.uri(),
            "description": {
                "en": "English description",
                "ru": "Русское описание",
            },
            "link": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": fake.numeric.integer_number(1, 100),
        }

        doc_id = await projects_crud.create(test_data)
        assert ObjectId.is_valid(doc_id)

    async def test_read_all_with_english_lang(self, projects_crud, fake):
        test_data = {
            "title": {"en": "Test EN", "ru": "Test RU"},
            "thumbnail": fake.internet.uri(),
            "image": fake.internet.uri(),
            "description": {"en": "Desc EN", "ru": "Desc RU"},
            "link": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": 50,
        }
        await projects_crud.create(test_data)

        results = await projects_crud.read_all("en", "date_desc")
        assert len(results) == 1
        assert results[0]["title"] == "Test EN"

    async def test_read_all_sorted_by_popularity(self, projects_crud, fake):
        for popularity in [10, 30, 20]:
            test_data = {
                "title": {
                    "en": f"Project {popularity}",
                    "ru": f"Проект {popularity}",
                },
                "thumbnail": fake.internet.uri(),
                "image": fake.internet.uri(),
                "description": {
                    "en": f"Description {popularity}",
                    "ru": f"Описание {popularity}",
                },
                "link": fake.internet.uri(),
                "date": datetime.now(),
                "popularity": popularity,
            }
            await projects_crud.create(test_data)

        results = await projects_crud.read_all("en", "popularity_desc")
        assert len(results) == 3

    async def test_read_all_with_invalid_lang(self, projects_crud, fake):
        test_data = {
            "title": {
                "en": "English Title",
                "ru": "Русский заголовок",
            },
            "thumbnail": fake.internet.uri(),
            "image": fake.internet.uri(),
            "description": {
                "en": "English desc",
                "ru": "Русское описание",
            },
            "link": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": 50,
        }
        await projects_crud.create(test_data)

        results = await projects_crud.read_all("fr", "date_desc")
        assert len(results) == 1
        assert "title" in results[0]

    async def test_read_by_id_with_lang(self, projects_crud, fake):
        test_data = {
            "title": {"en": "English Title", "ru": "Русский заголовок"},
            "thumbnail": fake.internet.uri(),
            "image": fake.internet.uri(),
            "description": {"en": "English desc", "ru": "Русское описание"},
            "link": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": 50,
        }
        doc_id = await projects_crud.create(test_data)

        result = await projects_crud.read_by_id(doc_id, "en")
        assert result is not None
        assert result["title"] == "English Title"

    async def test_read_by_id_not_found(self, projects_crud):
        result = await projects_crud.read_by_id(str(ObjectId()), "en")
        assert result is None

    async def test_update_project(self, projects_crud, fake):
        test_data = {
            "title": {
                "en": "Old Title",
                "ru": "Старый заголовок",
            },
            "thumbnail": fake.internet.uri(),
            "image": fake.internet.uri(),
            "description": {
                "en": "Old description",
                "ru": "Старое описание",
            },
            "link": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": 50,
        }
        doc_id = await projects_crud.create(test_data)

        await projects_crud.update(doc_id, {"title.en": "New Title"})

        result = await projects_crud.read_by_id(doc_id, "en")
        assert result["title"] == "New Title"

    async def test_delete_project(self, projects_crud, fake):
        test_data = {
            "title": {"en": "Test Project", "ru": "Тестовый проект"},
            "thumbnail": fake.internet.uri(),
            "image": fake.internet.uri(),
            "description": {
                "en": "Test description",
                "ru": "Тестовое описание",
            },
            "link": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": 50,
        }
        doc_id = await projects_crud.create(test_data)

        deleted = await projects_crud.delete(doc_id)
        assert deleted is True

        result = await projects_crud.read_by_id(doc_id, "en")
        assert result is None

    async def test_delete_project_not_found(self, projects_crud):
        deleted = await projects_crud.delete(str(ObjectId()))
        assert deleted is False
