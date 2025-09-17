from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from settings import settings


class PublicationCreateForm(BaseModel):
    """Form model for creating publication via multipart/form-data.

    Attributes:
        title_en: English publication title.
        title_ru: Russian publication title.
        page: Publication page URL.
        site: Site URL.
        rating: Publication rating (-1000-1000).
        date: Publication date in ISO format.
    """

    title_en: str = Field(
        min_length=settings.MIN_TITLE_LENGTH,
        max_length=settings.MAX_TITLE_LENGTH,
        json_schema_extra={"example": "Publication Title EN"}
    )
    title_ru: str = Field(
        min_length=settings.MIN_TITLE_LENGTH,
        max_length=settings.MAX_TITLE_LENGTH,
        json_schema_extra={"example": "Заголовок публикации РУ"}
    )
    page: HttpUrl = Field(
        json_schema_extra={"example": "https://example.com/page"}
    )
    site: HttpUrl = Field(
        json_schema_extra={"example": "https://example.com"}
    )
    rating: int = Field(
        ge=settings.MIN_PUBLICATIONS_RATING_BOUNDARY,
        le=settings.MAX_PUBLICATIONS_RATING_BOUNDARY,
        json_schema_extra={"example": 0}
    )
    date: datetime = Field(default_factory=datetime.now)


class PublicationUpdateForm(BaseModel):
    """Form model for creating publication via multipart/form-data.

    Attributes:
        title_en: English publication title.
        title_ru: Russian publication title.
        page: Publication page URL.
        site: Site URL.
        rating: Publication rating (-1000-1000).
        date: Publication date in ISO format.
    """

    title_en: str = Field(
        "Publication Title EN",
        min_length=settings.MIN_TITLE_LENGTH,
        max_length=settings.MAX_TITLE_LENGTH,
        json_schema_extra={"example": "Publication Title EN"}
    )
    title_ru: str = Field(
        "Заголовок публикации РУ",
        min_length=settings.MIN_TITLE_LENGTH,
        max_length=settings.MAX_TITLE_LENGTH,
        json_schema_extra={"example": "Заголовок публикации РУ"}
    )
    page: HttpUrl = Field(
        "https://example.com/page",
        json_schema_extra={"example": "https://example.com/page"}
    )
    site: HttpUrl = Field(
        "https://example.com",
        json_schema_extra={"example": "https://example.com"}
    )
    rating: int = Field(
        0,
        ge=settings.MIN_PUBLICATIONS_RATING_BOUNDARY,
        le=settings.MAX_PUBLICATIONS_RATING_BOUNDARY,
        json_schema_extra={"example": 0}
    )