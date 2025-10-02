from datetime import datetime
from typing import Annotated, Optional

from fastapi import Form, HTTPException, status
from pydantic import BaseModel, Field, HttpUrl, ValidationError

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
    popularity: int = Field(
        0,
        ge=settings.MIN_POPULARITY_BOUNDARY,
        le=settings.MAX_POPULARITY_BOUNDARY,
    )

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
        popularity: int = Form(json_schema_extra={"example": 0}),
    ):
        try:
            if link:
                HttpUrl(link)

            if len(title_en) > settings.MAX_TITLE_LENGTH:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Title EN too long, max {settings.MAX_TITLE_LENGTH} chars",
                )
            if len(description_en) > settings.MAX_DESCRIPTION_LENGTH:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Description EN too long, max {settings.MAX_DESCRIPTION_LENGTH} chars",
                )
            if len(title_ru) > settings.MAX_TITLE_LENGTH:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Title RU too long, max {settings.MAX_TITLE_LENGTH} chars",
                )
            if len(description_ru) > settings.MAX_DESCRIPTION_LENGTH:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Description RU too long, max {settings.MAX_DESCRIPTION_LENGTH} chars",
                )
            return cls(
                title_en=title_en,
                description_en=description_en,
                title_ru=title_ru,
                description_ru=description_ru,
                link=link,
                popularity=popularity,
            )
        except ValidationError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid URL format",
            )


class ProjectUpdateRequest(BaseModel):
    """Request model for updating project information.

    Attributes:
        title_en (Optional[str]): English title of the project.
        description_en (Optional[str]): English description of the project.
        title_ru (Optional[str]): Russian title of the project.
        description_ru (Optional[str]): Russian description of the project.
        link (Optional[HttpUrl]): Project URL.
        popularity (Optional[int]): Popularity score within defined boundaries.
    """

    title_en: Optional[str] = Field(None, max_length=settings.MAX_TITLE_LENGTH)
    description_en: Optional[str] = Field(
        None, max_length=settings.MAX_DESCRIPTION_LENGTH
    )
    title_ru: Optional[str] = Field(None, max_length=settings.MAX_TITLE_LENGTH)
    description_ru: Optional[str] = Field(
        None, max_length=settings.MAX_DESCRIPTION_LENGTH
    )
    link: Optional[HttpUrl] = Field(None)
    popularity: Optional[int] = Field(
        0,
        ge=settings.MIN_POPULARITY_BOUNDARY,
        le=settings.MAX_POPULARITY_BOUNDARY,
    )
