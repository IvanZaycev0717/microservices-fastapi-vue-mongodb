import logging
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from datetime import datetime

from comments_admin.db_connection import get_db_session
from comments_admin.schemas import CommentResponse, CreateCommentForm
from content_admin.dependencies import get_logger_factory

from settings import settings
from comments_admin.crud import CommentsCRUD


router = APIRouter(prefix="/comments")


from fastapi import HTTPException, status


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_comment(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    comment: Annotated[CreateCommentForm, Form()],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    try:
        comments_crud = CommentsCRUD(db_session)
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
        comment_id = await comments_crud.create_comment(comment_data)
        logger.info(f"Comment created successfully with id={comment_id}")
        return {"message": f"Comment with id={comment_id} was created"}

    except ValueError as e:
        logger.error(f"Validation error creating comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )

    except Exception as e:
        logger.error(f"Unexpected error creating comment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=list[CommentResponse])
async def get_all_comments(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    try:
        crud = CommentsCRUD(db_session)
        comments = await crud.read_all_comments()
        logger.info(f"Retrieved {len(comments)} comments")
        return comments
    except ValueError as e:
        logger.error(f"Error retrieving comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving comments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
