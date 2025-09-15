from typing import Any, Dict, List

from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase

from services.logger import get_logger
from settings import settings


logger = get_logger(settings.CONTENT_SERVICE_CERTIFICATES_NAME)


class CertificatesCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.certificates

    async def read_all(self, sort: str = "date_desc") -> List[Dict[str, Any]]:
        try:
            if sort.startswith("date"):
                sort_field = "date"
                sort_direction = -1 if sort.endswith("desc") else 1
            else:
                sort_field = "popularity"
                sort_direction = 1 if sort.endswith("desc") else -1

            cursor = self.collection.find({}).sort(sort_field, sort_direction)
            results = await cursor.to_list(length=None)

            transformed_results = []
            for item in results:
                transformed_results.append(
                    {
                        "id": str(item["_id"]),
                        "thumb": item["thumb"],
                        "src": item["src"],
                        "date": item["date"].isoformat()
                        if hasattr(item["date"], "isoformat")
                        else item["date"],
                        "popularity": item["popularity"],
                        "alt": item["alt"],
                    }
                )
            return transformed_results
        except Exception as e:
            logger.exception(f"Database error in read_all: {e}")
            raise
    
    async def create(self, certificate_data: dict[str, Any]) -> str:
        """Create new certificate document in MongoDB collection.

        Args:
            certificate_data: Dictionary with certificate data.

        Returns:
            str: String representation of inserted document's ObjectId.

        Raises:
            Exception: If database operation fails.
        """
        try:
            result = await self.collection.insert_one(certificate_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.exception(f"Database error in create: {e}")
            raise
