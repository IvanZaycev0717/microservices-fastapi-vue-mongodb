import logging
from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from content_admin.crud.projects import ProjectsCRUD
from content_admin.dependencies import get_logger_dependency, get_projects_crud
from content_admin.models.projects import ProjectResponse

router = APIRouter(prefix="/projects")


class Language(StrEnum):
    EN = "en"
    RU = "ru"


class SortOrder(StrEnum):
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    POPULARITY = "popularity"


@router.get("", response_model=list[ProjectResponse])
async def get_projects(
    projects_crud: Annotated[ProjectsCRUD, Depends(get_projects_crud)],
    logger: Annotated[logging.Logger, Depends(get_logger_dependency)],
    lang: Language = Language.EN,
    sort: SortOrder = SortOrder.DATE_DESC,
):
    try:
        result = await projects_crud.read_all(lang=lang, sort=sort.value)
        if not result:
            raise HTTPException(status_code=404, detail="Projects not found")
        logger.info("Projects data fetched successfully")
        return result
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching projects data",
        )
