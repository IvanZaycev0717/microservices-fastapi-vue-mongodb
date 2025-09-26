from datetime import datetime

from src.auth_admin.models.user_role import UserRole


class TestAuthCRUD:
    async def test_create_user(self, auth_crud, fake):
        email = fake.person.email()
        password_hash = fake.text.word()
        roles = [UserRole.USER, UserRole.ADMIN]

        user = await auth_crud.create_user(email, password_hash, roles)

        assert user.email == email
        assert user.password_hash == password_hash
        assert user.roles == [UserRole.USER.value, UserRole.ADMIN.value]
        assert user.is_banned is False
        assert isinstance(user.created_at, datetime)

    async def test_create_user_default_roles(self, auth_crud, fake):
        email = fake.person.email()
        password_hash = fake.text.word()

        user = await auth_crud.create_user(email, password_hash, [])

        assert user.roles == [UserRole.USER.value]

    async def test_get_user_by_email_found(self, auth_crud, fake):
        email = fake.person.email()
        password_hash = fake.text.word()

        await auth_crud.create_user(email, password_hash, [UserRole.USER])
        user = await auth_crud.get_user_by_email(email)

        assert user is not None
        assert user.email == email

    async def test_get_user_by_email_not_found(self, auth_crud, fake):
        user = await auth_crud.get_user_by_email("nonexistent@test.com")
        assert user is None

    async def test_get_all_users(self, auth_crud, fake):
        for i in range(3):
            email = f"user{i}@test.com"
            password_hash = fake.text.word()
            await auth_crud.create_user(email, password_hash, [UserRole.USER])

        users = await auth_crud.get_all_users()
        assert len(users) == 3
        assert all(user.email.startswith("user") for user in users)

    async def test_get_all_users_empty(self, auth_crud):
        users = await auth_crud.get_all_users()
        assert len(users) == 0

    async def test_update_user(self, auth_crud, fake):
        email = fake.person.email()
        password_hash = fake.text.word()

        await auth_crud.create_user(email, password_hash, [UserRole.USER])

        updated_user = await auth_crud.update_user(email, {"is_banned": True})
        assert updated_user is not None
        assert updated_user.is_banned is True
        assert updated_user.email == email

    async def test_update_user_not_found(self, auth_crud):
        updated_user = await auth_crud.update_user(
            "nonexistent@test.com", {"is_banned": True}
        )
        assert updated_user is None

    async def test_update_user_last_login(self, auth_crud, fake):
        email = fake.person.email()
        password_hash = fake.text.word()

        await auth_crud.create_user(email, password_hash, [UserRole.USER])

        user = await auth_crud.update_user_last_login(email)
        assert user is not None
        assert user.last_login_at is not None
        assert isinstance(user.last_login_at, datetime)

    async def test_delete_user_by_email(self, auth_crud, fake):
        email = fake.person.email()
        password_hash = fake.text.word()

        await auth_crud.create_user(email, password_hash, [UserRole.USER])

        deleted = await auth_crud.delete_user_by_email(email)
        assert deleted is True

        user = await auth_crud.get_user_by_email(email)
        assert user is None

    async def test_delete_user_not_found(self, auth_crud):
        deleted = await auth_crud.delete_user_by_email("nonexistent@test.com")
        assert deleted is False
