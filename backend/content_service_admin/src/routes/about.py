from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from services.crud.about import AboutCRUD

router = APIRouter(prefix="/about", tags=["about"])


async def get_about_crud(request: Request) -> AboutCRUD:
    db = request.app.state.mongo_db
    return AboutCRUD(db)


@router.get("/", response_model=List[dict])
async def get_about_content(
    lang: Optional[str] = Query(None), about_crud: AboutCRUD = Depends(get_about_crud)
):
    try:
        result = await about_crud.fetch(lang)
        if not result:
            raise HTTPException(status_code=404, detail="About content not found")
        return result
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching about content"
        )
