from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator

from settings import settings


class CreateCommentForm(BaseModel):
    """Модель для создания нового комментария"""

    project_id: str = Field(
        pattetn=settings.MONGO_ID_VALID_ID_REGEXP,
        description="ID проекта, к которому относится комментарий",
        json_schema_extra={"example": "68d0f79576dcb44be4b8315f"},
    )
    author_id: str = Field(
        pattetn=settings.MONGO_ID_VALID_ID_REGEXP,
        description="ID автора комментария",
        json_schema_extra={"example": "68d13f82ea73fb8fa3a60314"},
    )
    author_email: EmailStr = Field(
        max_length=settings.MAX_EMAIL_LENGHT,
        description="Email автора комментария",
        json_schema_extra={"example": "user@example.com"},
    )
    comment_text: str = Field(
        min_length=settings.MIN_COMMENT_LENGTH,
        max_length=settings.MAX_COMMENT_LENGTH,
        description="Текст комментария",
        json_schema_extra={"example": "Отличный проект!"},
    )
    parent_comment_id: int | None = Field(
        None, description="ID родительского комментария (если это ответ)"
    )

    @field_validator('parent_comment_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        return None if v == "" else v

class CommentResponse(BaseModel):
    id: int
    project_id: str
    author_id: str
    author_email: str
    comment_text: str
    created_at: datetime
    parent_comment_id: int | None
    likes: int
    dislikes: int
