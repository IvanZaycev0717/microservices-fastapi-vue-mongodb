from typing import Any, Optional

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase


class CertificatesCRUD:
    def __init__(self, db: AsyncDatabase):
        self.collection: AsyncCollection = db.certificates

    # CREATE
    async def create(self, certificate_data: dict[str, Any]) -> str:
        """Create new certificate document in MongoDB collection.

        Args:
            certificate_data: dictionary with certificate data.

        Returns:
            str: String representation of inserted document's ObjectId.

        Raises:
            Exception: If database operation fails.
        """
        result = await self.collection.insert_one(certificate_data)
        return str(result.inserted_id)

    # READ
    async def read_all(self, sort: str = "date_desc") -> list[dict[str, Any]]:
        if sort.startswith("date"):
            sort_field = "date"
            sort_direction = DESCENDING if sort.endswith("desc") else ASCENDING
        else:
            sort_field = "popularity"
            sort_direction = DESCENDING

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

    async def read_one_by_id(
        self, certificate_id: str
    ) -> Optional[dict[str, Any]]:
        """Get single certificate by ID.

        Args:
            certificate_id: MongoDB document ID as string.

        Returns:
            Optional[dict]: Certificate data if found, None otherwise.

        Raises:
            InvalidId: If certificate_id is not a valid ObjectId.
        """
        object_id = ObjectId(certificate_id)
        item = await self.collection.find_one({"_id": object_id})

        if not item:
            return None

        return {
            "id": str(item["_id"]),
            "src": item["src"],
            "thumb": item["thumb"],
            "date": item["date"].isoformat()
            if hasattr(item["date"], "isoformat")
            else item["date"],
            "popularity": item["popularity"],
            "alt": item["alt"],
        }

    # UPDATE
    async def update(
        self, certificate_id: str, update_data: dict[str, Any]
    ) -> bool:
        """Update certificate document by ID.

        Args:
            certificate_id: MongoDB document ID as string.
            update_data: dictionary with fields to update.

        Returns:
            bool: True if document was updated, False if not found.

        Raises:
            InvalidId: If certificate_id is not a valid ObjectId.
        """
        object_id = ObjectId(certificate_id)
        result = await self.collection.update_one(
            {"_id": object_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    # DELETE
    async def delete(self, certificate_id: str) -> bool:
        """Delete certificate document by ID.

        Args:
            certificate_id: MongoDB document ID as string.

        Returns:
            bool: True if document was deleted, False if not found.

        Raises:
            InvalidId: If certificate_id is not a valid ObjectId.
        """
        object_id = ObjectId(certificate_id)
        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0
