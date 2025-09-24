import logging
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from datetime import datetime

from comments_admin.db_connection import get_db_session
from comments_admin.schemas import CreateCommentForm
from comments_admin import crud
from content_admin.dependencies import get_logger_factory

from settings import settings


router = APIRouter(prefix="/comments")


@router.post("/")
async def create_comment(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    comment: Annotated[CreateCommentForm, Form()],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    logger.warning(str(comment.parent_comment_id))
    comment_data = {
        "project_id": comment.project_id,
        "author_id": comment.author_id,
        "author_email": comment.author_email,
        "comment_text": comment.comment_text,
        "created_at": datetime.now(),
        "parent_comment_id": comment.parent_comment_id,
        "likes": 0,
        "dislikes": 0,
    }
    comment_id = await crud.create_comment(
        db_session=db_session, comment_data=comment_data
    )
    return f"Comment with id={comment_id} was created"
