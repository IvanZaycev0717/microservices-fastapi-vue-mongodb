from typing import Literal
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict, field_validator

AllowedLanguage = Literal["en", "ru"]


class Translation(BaseModel):
    title: str = Field(min_length=1, max_length=255, example="Заголовок на языке")
    description: str = Field(min_length=1, max_length=1000, example="Описание на языке")



class AboutFullResponse(BaseModel):
    id: str = Field(alias="_id")
    image: str
    translations: dict[str, Translation]
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )


class AboutTranslatedResponse(BaseModel):
    id: str = Field(alias="_id")
    image: str
    title: str
    description: str
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )


class CreateAboutRequest(BaseModel):
    image: str = Field(min_length=1, example="image_1.jpg")
    translations: dict[AllowedLanguage, Translation] = Field(
        example={
            "en": {"title": "Some title EN", "description": "Some description EN"},
            "ru": {"title": "Название RU", "description": "Описание RU"},
        }
    )
