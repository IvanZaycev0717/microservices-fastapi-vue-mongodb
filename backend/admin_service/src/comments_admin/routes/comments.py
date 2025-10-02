import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession

from comments_admin.crud import CommentsCRUD
from comments_admin.dependencies import get_db_session
from comments_admin.schemas import (
    CommentResponse,
    CreateCommentForm,
    UpdateCommentRequest,
)
from content_admin.dependencies import get_logger_factory
from settings import settings

router = APIRouter(prefix="/comments")


from fastapi import HTTPException, status


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_comment(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    comment: CreateCommentForm,
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    """Create a new comment in the system.

    Args:
        db_session: Injected database session dependency.
        comment: Form data containing comment information.
        logger: Injected logger instance for comments admin.

    Returns:
        dict: Success message with created comment ID.

    Raises:
        HTTPException: If validation fails or internal error occurs.
    """
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


@router.get("", response_model=list[CommentResponse])
async def get_all_comments(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    """Retrieve all comments from the system.

    Args:
        db_session: Injected database session dependency.
        logger: Injected logger instance for comments admin.

    Returns:
        list[CommentResponse]: List of all comment responses.

    Raises:
        HTTPException: If retrieval fails or internal error occurs.
    """
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


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: Annotated[int, Path(ge=1)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    """Retrieve a specific comment by ID.

    Args:
        comment_id: ID of the comment to retrieve (must be >= 1).
        db_session: Injected database session dependency.
        logger: Injected logger instance for comments admin.

    Returns:
        CommentResponse: Requested comment data.

    Raises:
        HTTPException: If comment not found or internal error occurs.
    """
    try:
        crud = CommentsCRUD(db_session)
        comment = await crud.read_one_comment(comment_id)
        logger.info(f"Retrieved comment with id={comment_id}")
        return comment
    except ValueError as e:
        logger.error(f"Error retrieving comment {comment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except Exception as e:
        logger.error(
            f"Unexpected error retrieving comment {comment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/project/{project_id}", response_model=list[CommentResponse])
async def get_comments_by_project_id(
    project_id: Annotated[str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    """Retrieve all comments for a specific project.

    Args:
        project_id: ID of the project to retrieve comments for.
        db_session: Injected database session dependency.
        logger: Injected logger instance for comments admin.

    Returns:
        list[CommentResponse]: List of comment responses for the project.

    Raises:
        HTTPException: If project not found or internal error occurs.
    """
    try:
        crud = CommentsCRUD(db_session)
        comments = await crud.get_comments_by_project_id(project_id)
        logger.info(
            f"Retrieved {len(comments)} comments for project {project_id}"
        )
        return comments
    except ValueError as e:
        logger.error(
            f"Error retrieving comments for project {project_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except Exception as e:
        logger.error(
            f"Unexpected error retrieving comments for project {project_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.patch("/{comment_id}", response_model=dict)
async def update_comment(
    comment_id: Annotated[int, Path(ge=1)],
    update_data: UpdateCommentRequest,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    """Update comment text for a specific comment.

    Args:
        comment_id: ID of the comment to update (must be >= 1).
        update_data: Request data containing new comment text.
        db_session: Injected database session dependency.
        logger: Injected logger instance for comments admin.

    Returns:
        dict: Success message with updated comment ID.

    Raises:
        HTTPException: If comment not found or internal error occurs.
    """
    try:
        crud = CommentsCRUD(db_session)
        updated_id = await crud.update_comment(
            comment_id, update_data.new_text
        )
        logger.info(f"Comment with id={updated_id} updated successfully")
        return {"message": f"Comment with id={updated_id} was updated"}
    except ValueError as e:
        logger.error(f"Error updating comment {comment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except Exception as e:
        logger.error(
            f"Unexpected error updating comment {comment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: Annotated[int, Path(ge=1)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    """Delete a specific comment by ID.

    Args:
        comment_id: ID of the comment to delete (must be >= 1).
        db_session: Injected database session dependency.
        logger: Injected logger instance for comments admin.

    Returns:
        dict: Success message with deleted comment ID.

    Raises:
        HTTPException: If comment not found or internal error occurs.
    """
    try:
        crud = CommentsCRUD(db_session)
        deleted_id = await crud.delete_comment(comment_id)
        logger.info(f"Comment with id={deleted_id} deleted successfully")
        return {"message": f"Comment with id={deleted_id} was deleted"}
    except ValueError as e:
        logger.error(f"Error deleting comment {comment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except Exception as e:
        logger.error(
            f"Unexpected error deleting comment {comment_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.patch("/ban_user/{author_id}", status_code=status.HTTP_200_OK)
async def ban_user_comments(
    author_id: Annotated[str, Path(regex=settings.MONGO_ID_VALID_ID_REGEXP)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.COMMENTS_ADMIN_NAME)),
    ],
):
    """Ban user and update all their comments to default state.

    Args:
        author_id: ID of the user to ban.
        db_session: Injected database session dependency.
        logger: Injected logger instance for comments admin.

    Returns:
        dict: Success message with count of updated comments.

    Raises:
        HTTPException: If operation fails or internal error occurs.
    """
    try:
        crud = CommentsCRUD(db_session)
        updated_count = await crud.set_default_comments_of_banned_user(
            author_id
        )

        logger.info(
            f"Banned user {author_id}: updated {updated_count} comments"
        )
        return {
            "message": f"User {author_id} banned successfully",
            "updated_comments": updated_count,
        }

    except ValueError as e:
        logger.error(f"Error banning user {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error banning user {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
