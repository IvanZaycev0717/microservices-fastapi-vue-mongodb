from datetime import datetime

from bson import ObjectId


class TestCertificatesCRUD:
    async def test_create_certificate(self, certificates_crud, fake):
        test_data = {
            "thumb": fake.internet.uri(),
            "src": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": fake.numeric.integer_number(1, 100),
            "alt": fake.text.text(),
        }

        doc_id = await certificates_crud.create(test_data)
        assert ObjectId.is_valid(doc_id)

    async def test_read_all_sorted_by_date_desc(self, certificates_crud, fake):
        for i in range(3):
            test_data = {
                "thumb": fake.internet.uri(),
                "src": fake.internet.uri(),
                "date": datetime(2023, 1, i + 1),
                "popularity": 50,
                "alt": fake.text.text(),
            }
            await certificates_crud.create(test_data)

        results = await certificates_crud.read_all("date_desc")
        assert len(results) == 3
        assert "id" in results[0]
        assert "date" in results[0]

    async def test_read_all_sorted_by_popularity(
        self, certificates_crud, fake
    ):
        for popularity in [10, 30, 20]:
            test_data = {
                "thumb": fake.internet.uri(),
                "src": fake.internet.uri(),
                "date": datetime.now(),
                "popularity": popularity,
                "alt": fake.text.text(),
            }
            await certificates_crud.create(test_data)

        results = await certificates_crud.read_all("popularity_desc")
        assert len(results) == 3

    async def test_read_one_by_id_found(self, certificates_crud, fake):
        test_data = {
            "thumb": fake.internet.uri(),
            "src": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": 50,
            "alt": "Test alt text",
        }
        doc_id = await certificates_crud.create(test_data)

        result = await certificates_crud.read_one_by_id(doc_id)
        assert result is not None
        assert result["alt"] == "Test alt text"

    async def test_read_one_by_id_not_found(self, certificates_crud):
        result = await certificates_crud.read_one_by_id(str(ObjectId()))
        assert result is None

    async def test_update_certificate(self, certificates_crud, fake):
        test_data = {
            "thumb": fake.internet.uri(),
            "src": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": 50,
            "alt": "Old alt",
        }
        doc_id = await certificates_crud.create(test_data)

        updated = await certificates_crud.update(doc_id, {"alt": "New alt"})
        assert updated is True

    async def test_update_certificate_not_found(self, certificates_crud):
        updated = await certificates_crud.update(
            str(ObjectId()), {"alt": "New"}
        )
        assert updated is False

    async def test_delete_certificate(self, certificates_crud, fake):
        test_data = {
            "thumb": fake.internet.uri(),
            "src": fake.internet.uri(),
            "date": datetime.now(),
            "popularity": 50,
            "alt": fake.text.text(),
        }
        doc_id = await certificates_crud.create(test_data)

        deleted = await certificates_crud.delete(doc_id)
        assert deleted is True

    async def test_delete_certificate_not_found(self, certificates_crud):
        deleted = await certificates_crud.delete(str(ObjectId()))
        assert deleted is False
