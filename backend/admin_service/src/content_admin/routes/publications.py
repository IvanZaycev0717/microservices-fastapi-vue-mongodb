from bson import ObjectId
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from typing import Annotated, List, Dict, Any
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
from fastapi import status

from content_admin.models.publications import (
    PublicationCreateForm,
    PublicationUpdateForm,
)

router = APIRouter(prefix="/publications")


@router.get("")
async def get_publications(
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
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


@router.get("/{document_id}")
async def get_publication_by_id(
    document_id: str,
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
):
    try:
        
        result = await publications_crud.read_by_id(document_id)
        if not result:
            raise HTTPException(
                status_code=404, detail="Publication not found"
            )
        logger.info(f"Publication {document_id} fetched successfully")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(500, detail="Internal server error")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_publication(
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
    form_data: Annotated[PublicationCreateForm, Form()],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
):
    try:
        publication_data = {
            "title": {"en": form_data.title_en, "ru": form_data.title_ru},
            "page": str(form_data.page),
            "site": str(form_data.site),
            "rating": form_data.rating,
            "date": form_data.date,
        }
        result = await publications_crud.create(publication_data)
        return f"Publication created with _id={result}"
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(500, "Internal server error")


@router.patch("/{document_id}")
async def update_publication(
    document_id: str,
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
    form_data: Annotated[PublicationUpdateForm, Form()],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
):
    try:
        if not ObjectId.is_valid(document_id):
            raise HTTPException(404, f"Invalid Document ID': {document_id}")

        current_publication = await publications_crud.read_by_id(document_id)

        if not current_publication:
            raise HTTPException(
                404, f"Document with id {document_id} not found"
            )

        if form_data.title_en is None or form_data.title_en == "":
            form_data.title_en = current_publication["title"].get("en", "")
        if form_data.title_ru is None or form_data.title_ru == "":
            form_data.title_ru = current_publication["title"].get("ru", "")
        if form_data.page is None or form_data.page == "":
            form_data.page = str(current_publication["page"])
        if form_data.site is None or form_data.site == "":
            form_data.site = str(current_publication["site"])
        if form_data.rating is None or form_data.rating == "":
            form_data.rating = current_publication["rating"]

        update_data = {
            "title": {"en": form_data.title_en, "ru": form_data.title_ru},
            "page": str(form_data.page),
            "site": str(form_data.site),
            "rating": form_data.rating,
        }

        await publications_crud.update(document_id, update_data)
        return {
            "message": f"Publication with id={document_id} updated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(500, "Internal server error")


@router.delete("/{document_id}")
async def delete_publication(
    document_id: str,
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_PROJECTS_NAME)),
    ],
):
    try:
        publication = await publications_crud.read_by_id(document_id)
        if not publication:
            raise HTTPException(404, f"Publication with id={document_id} not found")

        deleted = await publications_crud.delete(document_id)
        if not deleted:
            raise HTTPException(500, "Failed to delete publication from database")
        
        deleted_message = f"Publication with id={document_id} has been deleted"
        logger.info(deleted_message)
        return deleted_message

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting publication: {e}")
        raise HTTPException(500, "Failed to delete publication")
