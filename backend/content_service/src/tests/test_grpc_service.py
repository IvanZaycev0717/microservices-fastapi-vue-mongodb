from unittest.mock import AsyncMock, patch

import pytest

from proto import content_pb2
from service.content_service import ContentService


class TestContentService:
    """Test gRPC service methods."""

    @pytest.mark.asyncio
    async def test_get_about(self):
        service = ContentService()
        mock_context = AsyncMock()

        with patch(
            "service.content_service.db_manager.get_about",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = [
                type(
                    "obj",
                    (object,),
                    {
                        "id": "test123",
                        "image_url": "test.jpg",
                        "translations": {
                            "en": type(
                                "obj",
                                (object,),
                                {"title": "Test", "description": "Test desc"},
                            )
                        },
                    },
                )()
            ]

            request = content_pb2.AboutRequest(lang="en")
            result = await service.GetAbout(request, mock_context)

            assert len(result.about) == 1
            assert result.about[0].title == "Test"
