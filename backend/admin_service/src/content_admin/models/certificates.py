from datetime import datetime
from fastapi import status

from fastapi import Form, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from settings import settings


class CertificateCreateForm(BaseModel):
    """Form model for creating certificate via multipart/form-data.

    Attributes:
        src: Image source path.
        thumb: Thumbnail image path.
        alt: Alternative text for image.
        date: Certificate date in ISO format.
        popularity: Popularity score.
    """
    date: datetime = Field(default_factory=datetime.now)
    popularity: int = Field(
        settings.MIN_POPULARITY_BOUNDARY,
        ge=settings.MIN_POPULARITY_BOUNDARY,
        le=settings.MAX_POPULARITY_BOUNDARY,
    )

    @classmethod
    def as_form(
        cls,
        popularity: int = Form(
            json_schema_extra={"example": settings.MIN_POPULARITY_BOUNDARY}
        ),
    ):
        try:
            return cls(
                popularity=popularity,
            )
        except Exception as e:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
