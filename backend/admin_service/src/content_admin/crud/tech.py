from base import BaseCRUD


class TechCRUD(BaseCRUD):
    """CRUD operations for about collection."""

    async def get_about_content(self) -> dict:
        """Get all about content."""
        return await self.get_all()
