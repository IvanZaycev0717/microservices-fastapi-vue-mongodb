from typing import List

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Kingdom(BaseModel):
    """Pydantic model representing a technical skill kingdom with its items.

    Defines the structure
    for a kingdom category and its associated technical skills.

    Attributes:
        kingdom: Name of the technical skill category.
        items: List of technical skills belonging to this kingdom.
    """

    kingdom: str
    items: List[str]


class SkillsUpdate(BaseModel):
    """Request model for updating kingdom skills as comma-separated string.

    Designed for simple form data submission
    where skills are provided as a single string.
    Empty string default allows for optional skills update.

    Attributes:
        skills: Comma-separated string of technical skills to update.
    """

    skills: str = ""


class TechResponse(BaseModel):
    """Complete response model for all technical skills organized by kingdoms.

    Contains every technical skill kingdom
    as a separate attribute with its items.
    Automatically handles MongoDB ObjectId conversion and serialization.

    Attributes:
        id: Document identifier (MongoDB ObjectId converted to string).
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

    Config:
        Supports field name aliasing and custom ObjectId JSON encoding.
    """

    id: str = Field(alias="_id")
    backend_kingdom: Kingdom
    database_kingdom: Kingdom
    frontend_kingdom: Kingdom
    desktop_kingdom: Kingdom
    devops_kingdom: Kingdom
    telegram_kingdom: Kingdom
    parsing_kingdom: Kingdom
    computerscience_kingdom: Kingdom
    gamedev_kingdom: Kingdom
    ai_kingdom: Kingdom

    @field_validator("id", mode="before")
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = ConfigDict(populate_by_name=True, json_encoders={ObjectId: str})
