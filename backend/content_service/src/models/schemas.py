from datetime import datetime

from pydantic import BaseModel, Field

from settings import settings


class Translation(BaseModel):
    """Multilingual content translations.

    Attributes:
        title: Translation title with length constraints.
        description: Translation description with length constraints.
    """

    title: str = Field(
        min_length=settings.MIN_TITLE_LENGTH,
        max_length=settings.MAX_TITLE_LENGTH,
    )
    description: str = Field(
        min_length=settings.MIN_TITLE_LENGTH,
        max_length=settings.MAX_DESCRIPTION_LENGTH,
    )


class AboutDocument(BaseModel):
    """About documents from MongoDB.

    Attributes:
        id: Document identifier.
        image_url: URL of the associated image.
        translations: Dictionary of translations keyed by language code.
    """

    id: str = Field(alias="_id")
    image_url: str
    translations: dict[str, Translation]


class TechKingdom(BaseModel):
    """Technology skill category.

    Attributes:
        kingdom: Name of the technical skill category.
        items: List of technical skills belonging to this kingdom.
    """

    kingdom: str
    items: list[str]


class TechDocument(BaseModel):
    """Tech document from MongoDB.

    Attributes:
        id: Document identifier.
        backend_kingdom: Backend development skills kingdom.
        database_kingdom: Database technologies kingdom.
        frontend_kingdom: Frontend development skills kingdom.
        desktop_kingdom: Desktop application skills kingdom.
        devops_kingdom: DevOps and infrastructure kingdom.
        telegram_kingdom: Telegram development kingdom.
        parsing_kingdom: Data parsing skills kingdom.
        computerscience_kingdom: Computer science fundamentals kingdom.
        gamedev_kingdom: Game development skills kingdom.
        ai_kingdom: Artificial intelligence skills kingdom.
    """

    id: str = Field(alias="_id")
    backend_kingdom: TechKingdom
    database_kingdom: TechKingdom
    frontend_kingdom: TechKingdom
    desktop_kingdom: TechKingdom
    devops_kingdom: TechKingdom
    telegram_kingdom: TechKingdom
    parsing_kingdom: TechKingdom
    computerscience_kingdom: TechKingdom
    gamedev_kingdom: TechKingdom
    ai_kingdom: TechKingdom


class ProjectDocument(BaseModel):
    """Project documents from MongoDB.

    Attributes:
        id: Document identifier.
        title: Multilingual project titles.
        description: Multilingual project descriptions.
        thumbnail: URL of project thumbnail image.
        image: URL of project main image.
        link: Project external link.
        date: Project creation date.
        popularity: Project popularity score.
    """

    id: str = Field(alias="_id")
    title: dict[str, str]
    description: dict[str, str]
    thumbnail: str
    image: str
    link: str
    date: datetime
    popularity: int = Field(
        ge=settings.MIN_POPULARITY_BOUNDARY,
        le=settings.MAX_POPULARITY_BOUNDARY,
    )


class CertificateDocument(BaseModel):
    """Certificate documents from MongoDB.

    Attributes:
        id: Document identifier.
        src: URL of certificate main image.
        thumb: URL of certificate thumbnail image.
        alt: Alternative text for certificate image.
        date: Certificate issue date.
        popularity: Certificate popularity score.
    """

    id: str = Field(alias="_id")
    src: str
    thumb: str
    alt: str
    date: datetime
    popularity: int = Field(
        ge=settings.MIN_POPULARITY_BOUNDARY,
        le=settings.MAX_POPULARITY_BOUNDARY,
    )


class PublicationDocument(BaseModel):
    """Publication documents from MongoDB.

    Attributes:
        id: Document identifier.
        title: Multilingual publication titles.
        page: Publication page URL.
        site: Publication site URL.
        rating: Publication rating score.
        date: Publication date.
    """

    id: str = Field(alias="_id")
    title: dict[str, str]
    page: str
    site: str
    rating: int = Field(
        ge=settings.MIN_PUBLICATIONS_RATING_BOUNDARY,
        le=settings.MAX_PUBLICATIONS_RATING_BOUNDARY,
    )
    date: datetime
