import logging
from enum import StrEnum

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from content_admin.crud.tech import TechCRUD
from content_admin.dependencies import get_logger_dependency, get_tech_crud
from content_admin.models.tech import SkillsUpdate, TechResponse

router = APIRouter(prefix="/technologies")


class KingdomName(StrEnum):
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
    tech_crud: TechCRUD = Depends(get_tech_crud),
    logger: logging.Logger = Depends(get_logger_dependency),
):
    try:
        tech_data = await tech_crud.read_all()
        logger.info("Tech skills fetched successfully")
        return tech_data
    except Exception as e:
        error_message = f"Failed to fetch technical skills: {str(e)}"
        logger.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_message
        )


@router.patch("/{kingdom_name}")
async def update_kingdom_items(
    kingdom_name: KingdomName,
    skills_data: SkillsUpdate,
    tech_crud: TechCRUD = Depends(get_tech_crud),
    logger: logging.Logger = Depends(get_logger_dependency),
):
    try:
        items_list = [skill.strip() for skill in skills_data.skills.split(",") if skill.strip()]
        success = await tech_crud.update_kingdom_items(kingdom_name.value, items_list)

        if success:
            logger.info(f"Updated {kingdom_name.value} kingdom skills")
            return {"status": "success", "updated_skills": items_list}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Kingdom not found or no changes made"
            )

    except Exception as e:
        logger.error(f"Failed to update {kingdom_name.value}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
