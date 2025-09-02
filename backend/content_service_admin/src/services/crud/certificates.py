from typing import Any, Dict, List, Optional

from base import BaseCRUD
from pymongo.asynchronous.collection import AsyncCollection


class CertificatesCRUD(BaseCRUD):
    """CRUD operations for certificates collection with sorting support."""

    def __init__(self, collection: AsyncCollection):
        super().__init__(collection)

    async def get_all_certificates(
        self, sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all certificates with optional sorting.

        Args:
            sort (Optional[str]): Sorting option.
                Options: 'date_desc',
                'date_asc', 'popularity_desc', 'popularity_asc'
                Defaults to None (no sorting).

        Returns:
            List[Dict]: List of certificates.
        """
        sort_mapping = {
            "date_desc": [("date", -1)],
            "date_asc": [("date", 1)],
            "popularity_desc": [("popularity", -1)],
            "popularity_asc": [("popularity", 1)],
            None: None,
        }

        sort_criteria = sort_mapping.get(sort)

        if sort_criteria:
            cursor = self.collection.find({}).sort(sort_criteria)
        else:
            cursor = self.collection.find({})

        certificates = await cursor.to_list(length=None)

        for cert in certificates:
            cert.pop("_id", None)

        return certificates

    async def get_certificates_by_popularity_range(
        self, min_popularity: int,
        max_popularity: int,
        sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get certificates within popularity range.

        Args:
            min_popularity (int): Minimum popularity value.
            max_popularity (int): Maximum popularity value.
            sort (Optional[str]): Sorting option.

        Returns:
            List[Dict]: Filtered certificates.
        """
        filter_query = {
            "popularity": {"$gte": min_popularity, "$lte": max_popularity}}

        sort_mapping = {
            "date_desc": [("date", -1)],
            "date_asc": [("date", 1)],
            "popularity_desc": [("popularity", -1)],
            "popularity_asc": [("popularity", 1)],
            None: None,
        }

        sort_criteria = sort_mapping.get(sort)

        if sort_criteria:
            cursor = self.collection.find(filter_query).sort(sort_criteria)
        else:
            cursor = self.collection.find(filter_query)

        certificates = await cursor.to_list(length=None)

        for cert in certificates:
            cert.pop("_id", None)

        return certificates

    async def get_certificates_by_year(
        self, year: int, sort: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get certificates from specific year.

        Args:
            year (int): Year to filter by.
            sort (Optional[str]): Sorting option.

        Returns:
            List[Dict]: Certificates from specified year.
        """
        # Фильтр по году (дата начинается с указанного года)
        filter_query = {
            "date": {
                "$gte": f"{year}-01-01T00:00:00.000Z",
                "$lt": f"{year + 1}-01-01T00:00:00.000Z",
            }
        }

        sort_mapping = {
            "date_desc": [("date", -1)],
            "date_asc": [("date", 1)],
            "popularity_desc": [("popularity", -1)],
            "popularity_asc": [("popularity", 1)],
            None: None,
        }

        sort_criteria = sort_mapping.get(sort)

        if sort_criteria:
            cursor = self.collection.find(filter_query).sort(sort_criteria)
        else:
            cursor = self.collection.find(filter_query)

        certificates = await cursor.to_list(length=None)

        for cert in certificates:
            cert.pop("_id", None)

        return certificates

    async def get_most_popular_certificates(
        self, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top N most popular certificates.

        Args:
            limit (int): Number of certificates to return. Defaults to 5.

        Returns:
            List[Dict]: Most popular certificates.
        """
        cursor = self.collection.find({}).sort("popularity", -1).limit(limit)
        certificates = await cursor.to_list(length=None)

        for cert in certificates:
            cert.pop("_id", None)

        return certificates

    async def get_recent_certificates(
            self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most recent certificates.

        Args:
            limit (int): Number of certificates to return. Defaults to 5.

        Returns:
            List[Dict]: Most recent certificates.
        """
        cursor = self.collection.find({}).sort("date", -1).limit(limit)
        certificates = await cursor.to_list(length=None)

        for cert in certificates:
            cert.pop("_id", None)

        return certificates

    async def create_certificate(
        self, certificate_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new certificate.

        Args:
            certificate_data (Dict): Certificate data.

        Returns:
            Dict: Created certificate.

        Example:
            certificate_data = {
                "src": "New_Certificate",
                "thumb": "New_CertificateThumb",
                "date": "2025-08-15T00:00:00.000Z",
                "popularity": 90,
                "alt": "New Certificate"
            }
        """
        required_fields = ["src", "thumb", "date", "popularity", "alt"]
        for field in required_fields:
            if field not in certificate_data:
                raise ValueError(f"Missing required field: {field}")

        # Проверяем, не существует ли уже сертификат с таким src
        existing = await self.get_certificate_by_src(certificate_data["src"])
        if existing:
            raise ValueError(
                f"Certificate with src '{certificate_data['src']}' already exists"
            )

        await self.collection.insert_one(certificate_data)

        # Возвращаем созданный документ без _id
        new_certificate = await self.get_certificate_by_src(certificate_data["src"])
        return new_certificate
