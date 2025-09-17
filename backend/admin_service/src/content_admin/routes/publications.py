from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pymongo.asynchronous.database import AsyncDatabase
from content_admin.crud.publications import PublicationsCRUD
from content_admin.dependencies import (
    get_publications_crud,
    Language,
    SortOrder,
)
from content_admin.dependencies import get_logger_factory
from settings import settings
import logging

router = APIRouter(prefix="/publications")


@router.get("")
async def get_publications(
    publications_crud: PublicationsCRUD = Depends(get_publications_crud),
    logger: logging.Logger = Depends(
        get_logger_factory(settings.CONTENT_SERVICE_PUBLICATIONS_NAME)
    ),
    lang: Language = Language.EACH,
    sort: SortOrder = SortOrder.DATE_DESC,
) -> List[Dict[str, Any]]:
    """Get all publications with language support and sorting."""
    try:
        results = await publications_crud.read_all(
            lang=lang.value, sort=sort.value
        )
        if not results:
            raise HTTPException(
                status_code=404, detail="Publications not found"
            )

        logger.info("Publications data fetched successfully")
        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
