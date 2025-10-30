import logging
from typing import Annotated, Any

from bson import ObjectId
from fastapi import APIRouter, Depends, Form, HTTPException, Path, status

from content_admin.crud.publications import PublicationsCRUD
from content_admin.dependencies import (
    Language,
    SortOrder,
    get_logger_factory,
    get_publications_crud,
)
from content_admin.models.publications import (
    PublicationCreateForm,
    PublicationUpdateForm,
)
from settings import settings

router = APIRouter(prefix="/publications")


@router.get("")
async def get_publications(
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
    logger: logging.Logger = Depends(
        get_logger_factory(settings.CONTENT_ADMIN_PUBLICATIONS_NAME)
    ),
    lang: Language = Language.EACH,
    sort: SortOrder = SortOrder.DATE_DESC,
) -> list[dict[str, Any]]:
    """Retrieve all publications with language and sorting options.

    Args:
        publications_crud: Injected publications CRUD dependency.
        logger: Injected logger instance for publications admin.
        lang: Language preference for publication data.
        sort: Sorting order for publications.

    Returns:
        list[dict[str, Any]]: list of publication data.

    Raises:
        HTTPException: If publications not found or internal error occurs.
    """
    try:
        results = await publications_crud.read_all(
            lang=lang.value, sort=sort.value
        )
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publications not found",
            )

        logger.info("Publications data fetched successfully")
        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{document_id}")
async def get_publication_by_id(
    document_id: Annotated[str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)],
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_ADMIN_PROJECTS_NAME)),
    ],
):
    """Retrieve a specific publication by ID.

    Args:
        document_id: ID of the publication to retrieve.
        publications_crud: Injected publications CRUD dependency.
        logger: Injected logger instance for publications admin.

    Returns:
        dict: Publication data if found.

    Raises:
        HTTPException: If publication not found or internal error occurs.
    """
    try:
        result = await publications_crud.read_by_id(document_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publication not found",
            )
        logger.info(f"Publication {document_id} fetched successfully")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_publication(
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
    form_data: Annotated[PublicationCreateForm, Form()],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_ADMIN_PROJECTS_NAME)),
    ],
):
    """Create a new publication.

    Args:
        publications_crud: Injected publications CRUD dependency.
        form_data: Form data containing publication information.
        logger: Injected logger instance for publications admin.

    Returns:
        str: Success message with created publication ID.

    Raises:
        HTTPException: If internal error occurs.
    """
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.patch("/{document_id}")
async def update_publication(
    document_id: Annotated[str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)],
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
    form_data: Annotated[PublicationUpdateForm, Form()],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_ADMIN_PROJECTS_NAME)),
    ],
):
    """Update publication information.

    Args:
        document_id: ID of the publication to update.
        publications_crud: Injected publications CRUD dependency.
        form_data: Form data containing publication update information.
        logger: Injected logger instance for publications admin.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If publication not found or internal error occurs.
    """
    try:
        if not ObjectId.is_valid(document_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invalid Document ID': {document_id}",
            )

        current_publication = await publications_crud.read_by_id(document_id)

        if not current_publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {document_id} not found",
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{document_id}")
async def delete_publication(
    document_id: Annotated[str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)],
    publications_crud: Annotated[
        PublicationsCRUD, Depends(get_publications_crud)
    ],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_ADMIN_PROJECTS_NAME)),
    ],
):
    """Delete a specific publication by ID.

    Args:
        document_id: ID of the publication to delete.
        publications_crud: Injected publications CRUD dependency.
        logger: Injected logger instance for publications admin.

    Returns:
        str: Success message.

    Raises:
        HTTPException: If publication not found or internal error occurs.
    """
    try:
        publication = await publications_crud.read_by_id(document_id)
        if not publication:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Publication with id={document_id} not found",
            )

        deleted = await publications_crud.delete(document_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete publication from database",
            )

        deleted_message = f"Publication with id={document_id} has been deleted"
        logger.info(deleted_message)
        return deleted_message

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting publication: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete publication",
        )
