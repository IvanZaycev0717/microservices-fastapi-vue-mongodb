import logging
from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from content_admin.crud.tech import TechCRUD
from content_admin.dependencies import get_logger_factory, get_tech_crud
from content_admin.models.tech import SkillsUpdate, TechResponse
from settings import settings

router = APIRouter(prefix="/technologies")


class KingdomName(StrEnum):
    """Enum representing available technical skill kingdoms.

    Each member corresponds to a category of technical skills
    with their database collection names.
    Used for validating and routing kingdom-specific operations.

    Values:
        BACKEND: Backend development technologies
        DATABASE: Database management systems
        FRONTEND: Frontend development frameworks
        DESKTOP: Desktop application development
        DEVOPS: DevOps and infrastructure tools
        TELEGRAM: Telegram bot development
        PARSING: Data parsing and scraping technologies
        COMPUTER_SCIENCE: Computer science fundamentals
        GAME_DEV: Game development technologies
        AI: Artificial intelligence and machine learning
    """

    BACKEND = "backend_kingdom"
    DATABASE = "database_kingdom"
    FRONTEND = "frontend_kingdom"
    DESKTOP = "desktop_kingdom"
    DEVOPS = "devops_kingdom"
    TELEGRAM = "telegram_kingdom"
    PARSING = "parsing_kingdom"
    COMPUTER_SCIENCE = "computerscience_kingdom"
    GAME_DEV = "gamedev_kingdom"
    AI = "ai_kingdom"


@router.get("", response_model=list[TechResponse])
async def get_all_tech(
    tech_crud: Annotated[TechCRUD, Depends(get_tech_crud)],
    logger: Annotated[
        logging.Logger, Depends(get_logger_factory(settings.CONTENT_SERVICE_TECH_NAME))
    ],
):
    """Retrieves all technical skills from the database.

    Fetches the complete list of technical skills stored in the database.
    Returns an array of tech skill objects with their details.

    Args:
        tech_crud: Dependency injection for TechCRUD database operations.
        logger: Dependency injection for logging instance.

    Returns:
        list[TechResponse]: List of all technical skills.

    Raises:
        HTTPException: 500 if database operation fails
        or unexpected error occurs.
    """
    try:
        tech_data = await tech_crud.read_all()
        logger.info("Tech skills fetched successfully")
        return tech_data
    except Exception as e:
        error_message = f"Failed to fetch technical skills: {str(e)}"
        logger.exception(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        )


@router.patch("/{kingdom_name}")
async def update_kingdom_items(
    kingdom_name: KingdomName,
    skills_data: SkillsUpdate,
    tech_crud: Annotated[TechCRUD, Depends(get_tech_crud)],
    logger: Annotated[
        logging.Logger, Depends(get_logger_factory(settings.CONTENT_SERVICE_TECH_NAME))
    ],
):
    """Updates technical skills for a specific kingdom.

    Replaces the skills list for a given kingdom
    with new skills provided as a comma-separated string.
    Validates kingdom name and processes
    the input string into a cleaned list of skills.

    Args:
        kingdom_name: Name of the kingdom to update (from path parameter).
        skills_data: Request body containing comma-separated skills string.
        tech_crud: Dependency injection for TechCRUD database operations.
        logger: Dependency injection for logging instance.

    Returns:
        dict: Success status and list of updated skills.

    Raises:
        HTTPException: 404 if kingdom not found or no changes made,
        500 for unexpected errors.
    """
    try:
        items_list = [
            skill.strip() for skill in skills_data.skills.split(",") if skill.strip()
        ]
        success = await tech_crud.update_kingdom_items(kingdom_name.value, items_list)

        if success:
            logger.info(f"Updated {kingdom_name.value} kingdom skills")
            return {"status": "success", "updated_skills": items_list}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kingdom not found or no changes made",
            )

    except Exception as e:
        logger.exception(f"Failed to update {kingdom_name.value}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
