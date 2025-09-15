import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, List, Dict, Any
from content_admin.dependencies import SortOrder, get_logger_factory
from content_admin.crud.certificates import CertificatesCRUD
from content_admin.dependencies import get_certificates_crud
from settings import settings

router = APIRouter(prefix="/certificates")


@router.get("")
async def get_certificates(
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.CONTENT_SERVICE_CERTIFICATES_NAME)),
    ],
    certificates_crud: Annotated[
        CertificatesCRUD, Depends(get_certificates_crud)
    ],
    sort: SortOrder = SortOrder.DATE_DESC,
) -> List[Dict[str, Any]]:
    try:
        results = await certificates_crud.read_all(sort=sort.value)
        if not results:
            raise HTTPException(
                status_code=404, detail="Certificates not found"
            )
        logger.info('All certificates successfully fetched')
        return results
    except HTTPException as e:
        logger.exception(e)
    except Exception as e:
        logger.exception(f"Database error: {e}")
        raise HTTPException(500, detail="Internal server error")
