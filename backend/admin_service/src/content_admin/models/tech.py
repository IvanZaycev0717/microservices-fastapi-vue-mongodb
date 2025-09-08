from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List
from bson import ObjectId


class Kingdom(BaseModel):
    kingdom: str
    items: List[str]

class SkillsUpdate(BaseModel):
    skills: str = ""


class TechResponse(BaseModel):
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
