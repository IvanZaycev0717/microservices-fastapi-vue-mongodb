from bson import ObjectId


class TestAboutCRUD:
    async def test_create_and_read(self, about_crud, fake):
        test_data = {
            "image_url": fake.internet.uri(),
            "translations": {
                "en": {"title": "Test EN", "description": "Desc EN"},
                "ru": {"title": "Test RU", "description": "Desc RU"},
            },
        }

        doc_id = await about_crud.create(test_data)
        assert ObjectId.is_valid(doc_id)

        result = await about_crud.read_one(doc_id)
        assert result["image_url"] == test_data["image_url"]
