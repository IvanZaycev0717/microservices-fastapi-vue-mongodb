from datetime import datetime
from bson import ObjectId


class TestPublicationsCRUD:
    async def test_create_publication(self, publications_crud, fake):
        test_data = {
            "title": {"en": "English Title", "ru": "Русский заголовок"},
            "page": fake.internet.uri(),
            "site": fake.internet.hostname(),
            "rating": fake.numeric.integer_number(1, 5),
            "date": datetime.now(),
        }

        doc_id = await publications_crud.create(test_data)
        assert ObjectId.is_valid(doc_id)

    async def test_read_all_with_english_lang(self, publications_crud, fake):
        test_data = {
            "title": {"en": "Test EN", "ru": "Test RU"},
            "page": fake.internet.uri(),
            "site": fake.internet.hostname(),
            "rating": 4,
            "date": datetime.now(),
        }
        await publications_crud.create(test_data)

        results = await publications_crud.read_all("en", "date_desc")
        assert len(results) == 1
        assert results[0]["title"] == "Test EN"

    async def test_read_all_with_russian_lang(self, publications_crud, fake):
        test_data = {
            "title": {"en": "Test EN", "ru": "Тест RU"},
            "page": fake.internet.uri(),
            "site": fake.internet.hostname(),
            "rating": 4,
            "date": datetime.now(),
        }
        await publications_crud.create(test_data)

        results = await publications_crud.read_all("ru", "date_desc")
        assert len(results) == 1
        assert results[0]["title"] == "Тест RU"

    async def test_read_all_with_invalid_lang(self, publications_crud, fake):
        test_data = {
            "title": {"en": "English Title", "ru": "Русский заголовок"},
            "page": fake.internet.uri(),
            "site": fake.internet.hostname(),
            "rating": 4,
            "date": datetime.now(),
        }
        await publications_crud.create(test_data)

        results = await publications_crud.read_all("fr", "date_desc")
        assert len(results) == 1
        assert "title" in results[0]

    async def test_read_all_sorted_by_rating(self, publications_crud, fake):
        for rating in [1, 5, 3]:
            test_data = {
                "title": {
                    "en": f"Publication {rating}",
                    "ru": f"Публикация {rating}",
                },
                "page": fake.internet.uri(),
                "site": fake.internet.hostname(),
                "rating": rating,
                "date": datetime.now(),
            }
            await publications_crud.create(test_data)

        results = await publications_crud.read_all("en", "rating_desc")
        assert len(results) == 3

    async def test_read_by_id(self, publications_crud, fake):
        test_data = {
            "title": {"en": "English Title", "ru": "Русский заголовок"},
            "page": fake.internet.uri(),
            "site": fake.internet.hostname(),
            "rating": 5,
            "date": datetime.now(),
        }
        doc_id = await publications_crud.create(test_data)

        result = await publications_crud.read_by_id(doc_id)
        assert result is not None
        assert result["rating"] == 5

    async def test_update_publication(self, publications_crud, fake):
        test_data = {
            "title": {"en": "Old Title", "ru": "Старый заголовок"},
            "page": fake.internet.uri(),
            "site": fake.internet.hostname(),
            "rating": 3,
            "date": datetime.now(),
        }
        doc_id = await publications_crud.create(test_data)

        await publications_crud.update(doc_id, {"rating": 5})

        result = await publications_crud.read_by_id(doc_id)
        assert result["rating"] == 5

    async def test_delete_publication(self, publications_crud, fake):
        test_data = {
            "title": {"en": "Test Publication", "ru": "Тестовая публикация"},
            "page": fake.internet.uri(),
            "site": fake.internet.hostname(),
            "rating": 4,
            "date": datetime.now(),
        }
        doc_id = await publications_crud.create(test_data)

        deleted = await publications_crud.delete(doc_id)
        assert deleted is True

        result = await publications_crud.read_by_id(doc_id)
        assert result is None

    async def test_delete_publication_not_found(self, publications_crud):
        deleted = await publications_crud.delete(str(ObjectId()))
        assert deleted is False
