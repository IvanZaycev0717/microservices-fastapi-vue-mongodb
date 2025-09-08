import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from content_admin.dependencies import get_tech_crud, get_logger_dependency
from content_admin.crud.tech import TechCRUD
from content_admin.models.tech import TechResponse

router = APIRouter(prefix="/technologies")


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
