from datetime import datetime
from typing import Annotated

from bson import ObjectId
from fastapi import Form
from pydantic import BaseModel, Field, HttpUrl, field_validator

from settings import settings


class ProjectCreateForm(BaseModel):
    """Form model for creating project via multipart/form-data.

    Attributes:
        title_en: English project title.
        description_en: English project description.
        title_ru: Russian project title.
        description_ru: Russian project description.
        link: Project link URL.
        date: Project date in ISO format.
    """

    title_en: Annotated[str, Field(max_length=settings.MAX_TITLE_LENGTH)] = (
        "Project Title EN"
    )
    description_en: Annotated[
        str, Field(max_length=settings.MAX_DESCRIPTION_LENGTH)
    ] = "Project Description EN"
    title_ru: Annotated[str, Field(max_length=settings.MAX_TITLE_LENGTH)] = (
        "Заголовок проекта РУ"
    )
    description_ru: Annotated[
        str, Field(max_length=settings.MAX_DESCRIPTION_LENGTH)
    ] = "Описание проекта РУ"
    link: HttpUrl = "https://example.com"
    date: datetime = Field(default_factory=datetime.now)

    @classmethod
    def as_form(
        cls,
        title_en: str = Form(
            json_schema_extra={"example": "Project Title EN"}
        ),
        description_en: str = Form(
            json_schema_extra={"example": "Project Description EN"}
        ),
        title_ru: str = Form(
            json_schema_extra={"example": "Заголовок проекта РУ"}
        ),
        description_ru: str = Form(
            json_schema_extra={"example": "Описание проекта РУ"}
        ),
        link: str = Form(json_schema_extra={"example": "https://example.com"}),
    ):
        return cls(
            title_en=title_en,
            description_en=description_en,
            title_ru=title_ru,
            description_ru=description_ru,
            link=link,
        )
