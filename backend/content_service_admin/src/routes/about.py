from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from services.crud.about import AboutCRUD

router = APIRouter(prefix="/about", tags=["about"])

AllowedLanguage = Literal['en', 'ru']


class Translation(BaseModel):
    title: str = Field(min_length=1, max_length=255, example="Заголовок на языке")
    description: str = Field(min_length=1, max_length=1000, example="Описание на языке")


class CreateAboutRequest(BaseModel):
    image: str = Field(min_length=1, example="image_1.jpg")
    translations: dict[AllowedLanguage, Translation] = Field(
        ...,
        example={
            "en": {
                "title": "Some title EN",
                "description": "Some description EN"
            },
            "ru": {
                "title": "Название RU",
                "description": "Описание RU"
            }
        }
    )

async def get_about_crud(request: Request) -> AboutCRUD:
    db = request.app.state.mongo_db
    return AboutCRUD(db)


@router.get("/", response_model=List[dict])
async def get_about_content(
    lang: Optional[str] = Query(None), about_crud: AboutCRUD = Depends(get_about_crud)
):
    try:
        result = await about_crud.read_all(lang)
        if not result:
            raise HTTPException(status_code=404, detail="About content not found")
        return result
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching about content"
        )

@router.post('/')
async def create_about_content(request: CreateAboutRequest, about_crud: AboutCRUD = Depends(get_about_crud)):
    result = await about_crud.create(request.model_dump(exclude_none=True))
    return f'A new document with _id={result} was inserted'
