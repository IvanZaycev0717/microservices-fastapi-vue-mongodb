from typing import Literal, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator

AllowedLanguage = Literal["en", "ru"]


class Translation(BaseModel):
    title: str = Field(min_length=1, max_length=255, example="Заголовок на языке")
    description: str = Field(min_length=1, max_length=1000, example="Описание на языке")


class AboutFullResponse(BaseModel):
    id: str = Field(alias="_id")
    image_url: str
    translations: dict[str, Translation]

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = ConfigDict(populate_by_name=True, json_encoders={ObjectId: str})


class AboutTranslatedResponse(BaseModel):
    id: str = Field(alias="_id")
    image_url: str
    title: str
    description: str

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = ConfigDict(populate_by_name=True, json_encoders={ObjectId: str})


class CreateAboutRequest(BaseModel):
    image_url: str = Field(min_length=3)
    translations: dict[AllowedLanguage, Translation] = Field(
        example={
            "en": {"title": "Some title EN", "description": "Some description EN"},
            "ru": {"title": "Название RU", "description": "Описание RU"},
        }
    )


class AboutUpdateForm(BaseModel):
    title_en: Optional[str] = Field('Title EN')
    description_en: Optional[str] = Field('Description EN')
    title_ru: Optional[str] = Field('Заголовок РУ')
    description_ru: Optional[str] = Field('Описание РУ')

class AboutUpdateRequest(BaseModel):
    id: str = Field(description="MongoDB ObjectId of the document to update")
    image_url: Optional[str] = Field(None, description="New image URL")
    translations: Optional[dict[str, dict[str, str]]] = Field(
        None, 
        description="Translations object with language keys"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "68badb9576603121bb49626d",
                "image_url": "http://localhost:9000/about/new_image.webp",
                "translations": {
                    "en": {
                        "title": "Updated title EN",
                        "description": "Updated description EN"
                    },
                    "ru": {
                        "title": "Обновленное название RU",
                        "description": "Обновленное описание RU"
                    }
                }
            }
        }
