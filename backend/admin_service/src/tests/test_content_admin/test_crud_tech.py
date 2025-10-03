class TestTechCRUD:
    async def test_read_all_empty(self, tech_crud):
        results = await tech_crud.read_all()
        assert len(results) == 0

    async def test_update_kingdom_items(self, tech_crud):
        await tech_crud.collection.insert_one(
            {
                "frontend_kingdom": {
                    "kingdom": "Frontend",
                    "items": ["React", "Vue"],
                }
            }
        )

        updated = await tech_crud.update_kingdom_items(
            "frontend_kingdom", ["React", "Vue", "Angular", "Svelte"]
        )
        assert updated is True

        result = await tech_crud.collection.find_one()
        assert result["frontend_kingdom"]["items"] == [
            "React",
            "Vue",
            "Angular",
            "Svelte",
        ]

    async def test_update_kingdom_items_new_kingdom(self, tech_crud):
        updated = await tech_crud.update_kingdom_items(
            "backend_kingdom", ["Node.js", "Python", "Java"]
        )
        assert updated is True

    async def test_update_kingdom_items_multiple_operations(self, tech_crud):
        await tech_crud.collection.insert_one(
            {
                "frontend_kingdom": {
                    "kingdom": "Frontend",
                    "items": ["React"],
                },
                "backend_kingdom": {
                    "kingdom": "Backend",
                    "items": ["Node.js"],
                },
            }
        )

        updated_frontend = await tech_crud.update_kingdom_items(
            "frontend_kingdom", ["React", "Vue", "Angular"]
        )
        assert updated_frontend is True

        updated_backend = await tech_crud.update_kingdom_items(
            "backend_kingdom", ["Node.js", "Python", "Java", "Go"]
        )
        assert updated_backend is True

        result = await tech_crud.collection.find_one()
        assert result["frontend_kingdom"]["items"] == [
            "React",
            "Vue",
            "Angular",
        ]
        assert result["backend_kingdom"]["items"] == [
            "Node.js",
            "Python",
            "Java",
            "Go",
        ]

    async def test_update_kingdom_items_returns_boolean(self, tech_crud):
        updated = await tech_crud.update_kingdom_items("test_kingdom", [])
        assert isinstance(updated, bool)
