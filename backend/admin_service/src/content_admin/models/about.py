from typing import Literal, Optional

from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field, field_validator

from settings import settings

AllowedLanguage = Literal["en", "ru"]


class Translation(BaseModel):
    """Pydantic model for multilingual content translations.

    Represents a single language translation with title and description fields.
    Includes length validation and example values for API documentation.

    Attributes:
        title: Translation title with length constraints (1-255 characters).
        description: Translation description
        with length constraints (1-1000 characters).
    """

    title: str = Field(
        min_length=1,
        max_length=settings.MAX_TITLE_LENGTH,
        example="Заголовок на языке",
    )
    description: str = Field(
        min_length=1,
        max_length=settings.MAX_DESCRIPTION_LENGTH,
        example="Описание на языке",
    )


class AboutFullResponse(BaseModel):
    """Response model for about content with full multilingual data.

    Includes complete document details with all available translations.
    Automatically converts MongoDB ObjectId to string
    and handles JSON serialization.

    Attributes:
        id: Document identifier (MongoDB ObjectId converted to string).
        image_url: URL of the associated image.
        translations: Dictionary of translations keyed by language code.

    Config:
        Supports population by field
        name and custom JSON encoders for ObjectId.
    """

    id: str = Field(alias="_id")
    image_url: str
    translations: dict[str, Translation]

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        return str(v)

    model_config = ConfigDict(populate_by_name=True)


class AboutTranslatedResponse(BaseModel):
    """Response model for about content translated to a specific language.

    Contains only the translated fields
    for a single language instead of full multilingual dictionary.
    Automatically handles ObjectId conversion
    and serialization for API responses.

    Attributes:
        id: Document identifier (MongoDB ObjectId converted to string).
        image_url: URL of the associated image.
        title: Translated title in the requested language.
        description: Translated description in the requested language.

    Config:
        Supports field name population and custom ObjectId JSON encoding.
    """

    id: str = Field(alias="_id")
    image_url: str
    title: str
    description: str

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        return str(v)

    model_config = ConfigDict(populate_by_name=True)


class CreateAboutRequest(BaseModel):
    image_url: str = Field(min_length=3)
    translations: dict[AllowedLanguage, Translation] = Field(
        example={
            "en": {
                "title": "Some title EN",
                "description": "Some description EN",
            },
            "ru": {"title": "Название RU", "description": "Описание RU"},
        }
    )


class AboutUpdateForm(BaseModel):
    """Request model for creating new about content.

    Validates data structure for creating
    about section entries with image and translations.
    Includes example values for API documentation and clear validation rules.

    Attributes:
        image_url: URL string for the associated image (min 3 characters).
        translations: Dictionary
        of translations mapped by allowed language codes.

    Example:
        Provides structured example with both English and Russian translations.
    """

    title_en: Optional[str] = Field(
        "Title EN", max_length=settings.MAX_TITLE_LENGTH
    )
    description_en: Optional[str] = Field(
        "Description EN", max_length=settings.MAX_DESCRIPTION_LENGTH
    )
    title_ru: Optional[str] = Field(
        "Заголовок РУ", max_length=settings.MAX_TITLE_LENGTH
    )
    description_ru: Optional[str] = Field(
        "Описание РУ", max_length=settings.MAX_DESCRIPTION_LENGTH
    )


class AboutCreateForm(BaseModel):
    """Form model for creating about content via multipart/form-data.

    Designed to handle
    form submissions with separate fields for each language translation.
    Includes class method to convert form data into Pydantic model instance.

    Attributes:
        title_en: English title with default value for documentation.
        description_en: English description with default value.
        title_ru: Russian title with default value.
        description_ru: Russian description with default value.

    Methods:
        as_form: Class method to transform Form parameters into model instance.
    """

    title_en: str = Field(
        "Title EN", max_length=settings.MAX_DESCRIPTION_LENGTH
    )
    description_en: str = Field(
        "Description EN", max_length=settings.MAX_DESCRIPTION_LENGTH
    )
    title_ru: str = Field(
        "Заголовок РУ", max_length=settings.MAX_DESCRIPTION_LENGTH
    )
    description_ru: str = Field(
        "Описание РУ", max_length=settings.MAX_DESCRIPTION_LENGTH
    )

    @classmethod
    def as_form(
        cls,
        title_en: str = Form(),
        description_en: str = Form(),
        title_ru: str = Form(),
        description_ru: str = Form(),
    ):
        return cls(
            title_en=title_en,
            description_en=description_en,
            title_ru=title_ru,
            description_ru=description_ru,
        )


class AboutUpdateRequest(BaseModel):
    """Request model for updating existing about content.

    Supports partial updates
    of image URL and/or translations for multiple languages.
    Includes comprehensive example for API documentation
    and optional field handling.

    Attributes:
        id: MongoDB ObjectId of the document to update.
        image_url: Optional new image URL for replacement.
        translations: Optional nested
        dictionary with language-specific translations.

    Config:
        Provides detailed example structure for clear API documentation.
    """

    id: str = Field(description="MongoDB ObjectId of the document to update")
    image_url: Optional[str] = Field(None, description="New image URL")
    translations: Optional[dict[str, dict[str, str]]] = Field(
        None, description="Translations object with language keys"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "68badb9576603121bb49626d",
                "image_url": "http://localhost:9000/about/new_image.webp",
                "translations": {
                    "en": {
                        "title": "Updated title EN",
                        "description": "Updated description EN",
                    },
                    "ru": {
                        "title": "Обновленное название RU",
                        "description": "Обновленное описание RU",
                    },
                },
            }
        }
