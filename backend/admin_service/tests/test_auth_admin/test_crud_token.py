from datetime import datetime, timedelta
from bson import ObjectId


class TestTokenCRUD:
    async def test_create_refresh_token(self, token_crud, fake):
        user_id = str(ObjectId())
        token = fake.text.word()
        expired_at = datetime.now() + timedelta(days=7)

        token_id = await token_crud.create_refresh_token(
            user_id, token, expired_at
        )

        assert token_id is not None
        assert ObjectId.is_valid(token_id)

    async def test_create_refresh_token_with_used_flag(self, token_crud, fake):
        user_id = str(ObjectId())
        token = fake.text.word()
        expired_at = datetime.now() + timedelta(days=7)

        token_id = await token_crud.create_refresh_token(
            user_id, token, expired_at, used=True
        )

        assert token_id is not None

    async def test_get_refresh_token_found(self, token_crud, fake):
        user_id = str(ObjectId())
        token = fake.text.word()
        expired_at = datetime.now() + timedelta(days=7)

        await token_crud.create_refresh_token(user_id, token, expired_at)
        token_doc = await token_crud.get_refresh_token(token)

        assert token_doc is not None
        assert token_doc["token"] == token
        assert token_doc["user_id"] == user_id
        assert token_doc["used"] is False

    async def test_get_refresh_token_not_found(self, token_crud, fake):
        token_doc = await token_crud.get_refresh_token("invalid_token")
        assert token_doc is None

    async def test_get_refresh_token_used(self, token_crud, fake):
        user_id = str(ObjectId())
        token = fake.text.word()
        expired_at = datetime.now() + timedelta(days=7)

        await token_crud.create_refresh_token(
            user_id, token, expired_at, used=True
        )
        token_doc = await token_crud.get_refresh_token(token)

        assert token_doc is None

    async def test_get_user_refresh_tokens(self, token_crud, fake):
        user_id = str(ObjectId())

        for i in range(3):
            token = f"token_{i}"
            expired_at = datetime.now() + timedelta(days=7)
            await token_crud.create_refresh_token(user_id, token, expired_at)

        tokens = await token_crud.get_user_refresh_tokens(user_id)
        assert len(tokens) == 3
        assert all(token["user_id"] == user_id for token in tokens)
        assert all(token["used"] is False for token in tokens)

    async def test_get_user_refresh_tokens_empty(self, token_crud):
        tokens = await token_crud.get_user_refresh_tokens(str(ObjectId()))
        assert len(tokens) == 0

    async def test_mark_token_as_used(self, token_crud, fake):
        user_id = str(ObjectId())
        token = fake.text.word()
        expired_at = datetime.now() + timedelta(days=7)

        await token_crud.create_refresh_token(user_id, token, expired_at)

        marked = await token_crud.mark_token_as_used(token)
        assert marked is True

        token_doc = await token_crud.get_refresh_token(token)
        assert token_doc is None

        token_doc = await token_crud.collection.find_one({"token": token})
        assert token_doc["used"] is True
        assert "used_at" in token_doc

    async def test_mark_token_as_used_not_found(self, token_crud):
        marked = await token_crud.mark_token_as_used("invalid_token")
        assert marked is False

    async def test_invalidate_user_tokens(self, token_crud, fake):
        user_id = str(ObjectId())

        for i in range(3):
            token = f"token_{i}"
            expired_at = datetime.now() + timedelta(days=7)
            await token_crud.create_refresh_token(user_id, token, expired_at)

        invalidated_count = await token_crud.invalidate_user_tokens(user_id)
        assert invalidated_count == 3

        tokens = await token_crud.get_user_refresh_tokens(user_id)
        assert len(tokens) == 0

        tokens = await token_crud.collection.find(
            {"user_id": user_id}
        ).to_list(length=None)
        assert all(token["used"] is True for token in tokens)
        assert all("invalidated_at" in token for token in tokens)

    async def test_invalidate_user_tokens_no_tokens(self, token_crud):
        invalidated_count = await token_crud.invalidate_user_tokens(
            str(ObjectId())
        )
        assert invalidated_count == 0

    async def test_delete_expired_tokens(self, token_crud, fake):
        user_id = str(ObjectId())

        expired_token = "expired_token"
        active_token = "active_token"

        await token_crud.create_refresh_token(
            user_id, expired_token, datetime.now() - timedelta(days=1)
        )
        await token_crud.create_refresh_token(
            user_id, active_token, datetime.now() + timedelta(days=7)
        )

        deleted_count = await token_crud.delete_expired_tokens()
        assert deleted_count == 1

        expired_doc = await token_crud.collection.find_one(
            {"token": expired_token}
        )
        active_doc = await token_crud.collection.find_one(
            {"token": active_token}
        )

        assert expired_doc is None
        assert active_doc is not None
