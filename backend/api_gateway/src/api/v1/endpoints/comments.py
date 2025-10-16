from fastapi import APIRouter, HTTPException, Depends, status
from grpc import RpcError
import grpc
from pydantic import BaseModel

from grpc_clients.comments_client import CommentsClient
from logger import get_logger
from api.v1.dependencies import get_comment_author, get_current_user

router = APIRouter()
logger = get_logger("CommentsEndpoints")
comments_client = CommentsClient()


# for OpenAPI only
class CommentCreateRequest(BaseModel):
    project_id: str
    comment_text: str
    parent_comment_id: int = None


class CommentUpdateRequest(BaseModel):
    new_text: str


@router.get("/comments")
async def get_all_comments():
    """
    Retrieve all comments from the system.

    Returns:
        dict: Dictionary containing a list of all comments with their details.

    Raises:
        HTTPException:
            - 500: If comments service is unavailable or internal error occurs

    Note:
        - Returns comprehensive comment data including engagement metrics (likes/dislikes)
        - Converts gRPC response to REST-friendly format
        - Handles optional parent_comment_id field appropriately
    """
    try:
        response = comments_client.get_all_comments()
        return {
            "comments": [
                {
                    "id": comment.id,
                    "project_id": comment.project_id,
                    "author_id": comment.author_id,
                    "author_email": comment.author_email,
                    "comment_text": comment.comment_text,
                    "created_at": comment.created_at,
                    "parent_comment_id": comment.parent_comment_id
                    if comment.parent_comment_id
                    else None,
                    "likes": comment.likes,
                    "dislikes": comment.dislikes,
                }
                for comment in response.comments
            ]
        }
    except RpcError as e:
        logger.error(
            f"gRPC error in get_all_comments: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comments service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_all_comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/comments/my")
async def get_my_comments(current_user: dict = Depends(get_current_user)):
    """
    Retrieve all comments made by the currently authenticated user.

    Args:
        current_user (dict): Authenticated user data from dependency.

    Returns:
        dict: Dictionary containing a list of the user's comments with details.

    Raises:
        HTTPException:
            - 401: If user is not authenticated (handled by get_current_user dependency)
            - 500: If comments service is unavailable or internal error occurs

    Note:
        - Returns empty list if no comments found for the user
        - Uses current user's ID to filter comments
        - Converts gRPC response to REST-friendly format
    """
    try:
        response = comments_client.get_comments_by_author_id(
            current_user["user_id"]
        )
        return {
            "comments": [
                {
                    "id": comment.id,
                    "project_id": comment.project_id,
                    "author_id": comment.author_id,
                    "author_email": comment.author_email,
                    "comment_text": comment.comment_text,
                    "created_at": comment.created_at,
                    "parent_comment_id": comment.parent_comment_id
                    if comment.parent_comment_id
                    else None,
                    "likes": comment.likes,
                    "dislikes": comment.dislikes,
                }
                for comment in response.comments
            ]
        }
    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return {"comments": []}
        logger.error(
            f"gRPC error in get_my_comments: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comments service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_my_comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/comments/project/{project_id}")
async def get_comments_by_project_id(project_id: str):
    """
    Retrieve all comments for a specific project.

    Args:
        project_id (str): The ID of the project to retrieve comments for.

    Returns:
        dict: Dictionary containing a list of project comments with details.

    Raises:
        HTTPException:
            - 500: If comments service is unavailable or internal error occurs

    Note:
        - Returns empty list if no comments found for the project
        - Converts gRPC response to REST-friendly format
        - Includes comment engagement metrics (likes/dislikes) in response
    """
    try:
        response = comments_client.get_comments_by_project_id(project_id)
        return {
            "comments": [
                {
                    "id": comment.id,
                    "project_id": comment.project_id,
                    "author_id": comment.author_id,
                    "author_email": comment.author_email,
                    "comment_text": comment.comment_text,
                    "created_at": comment.created_at,
                    "parent_comment_id": comment.parent_comment_id
                    if comment.parent_comment_id
                    else None,
                    "likes": comment.likes,
                    "dislikes": comment.dislikes,
                }
                for comment in response.comments
            ]
        }
    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return {"comments": []}
        logger.error(
            f"gRPC error in get_comments_by_project_id: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comments service unavailable",
        )
    except Exception as e:
        logger.exception(
            f"Unexpected error in get_comments_by_project_id: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/comments/{comment_id}")
async def get_comment(comment_id: int):
    """
    Retrieve a specific comment by its ID.

    Args:
        comment_id (int): The unique identifier of the comment to retrieve.

    Returns:
        dict: Dictionary containing the comment details.

    Raises:
        HTTPException:
            - 404: If comment with the specified ID is not found
            - 500: If comments service is unavailable or internal error occurs

    Note:
        - Returns comprehensive comment data including engagement metrics
        - Converts gRPC response to REST-friendly format
        - Handles optional parent_comment_id field appropriately
    """
    try:
        response = comments_client.get_comment(comment_id)
        comment = response.comment
        return {
            "id": comment.id,
            "project_id": comment.project_id,
            "author_id": comment.author_id,
            "author_email": comment.author_email,
            "comment_text": comment.comment_text,
            "created_at": comment.created_at,
            "parent_comment_id": comment.parent_comment_id
            if comment.parent_comment_id
            else None,
            "likes": comment.likes,
            "dislikes": comment.dislikes,
        }
    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        logger.error(f"gRPC error in get_comment: {e.code()} - {e.details()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comments service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/comments")
async def create_comment(
    comment_data: CommentCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new comment for a project.

    Args:
        comment_data (CommentCreateRequest): Comment creation data including text and project ID.
        current_user (dict): Authenticated user data from dependency.

    Returns:
        dict: Dictionary containing the created comment ID and status message.

    Raises:
        HTTPException:
            - 400: If request data is invalid (e.g., empty comment text)
            - 401: If user is not authenticated (handled by get_current_user dependency)
            - 500: If comments service is unavailable or internal error occurs

    Note:
        - Automatically sets author information from authenticated user
        - Supports both top-level comments and replies via parent_comment_id
    """
    try:
        response = comments_client.create_comment(
            project_id=comment_data.project_id,
            author_id=current_user["user_id"],
            author_email=current_user["email"],
            comment_text=comment_data.comment_text,
            parent_comment_id=comment_data.parent_comment_id,
        )
        return {"comment_id": response.comment_id, "message": response.message}
    except RpcError as e:
        if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.details()
            )
        logger.error(
            f"gRPC error in create_comment: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comments service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in create_comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    update_data: CommentUpdateRequest,
    current_user: dict = Depends(get_comment_author),
):
    """
    Update an existing comment's text.

    Args:
        comment_id (int): The unique identifier of the comment to update.
        update_data (CommentUpdateRequest): Update data containing the new comment text.
        current_user (dict): Authenticated user data from dependency (must be comment author).

    Returns:
        dict: Dictionary containing the updated comment ID and status message.

    Raises:
        HTTPException:
            - 400: If request data is invalid (e.g., empty comment text)
            - 403: If user is not the comment author (handled by get_comment_author dependency)
            - 404: If comment with the specified ID is not found
            - 500: If comments service is unavailable or internal error occurs

    Note:
        - Only allows comment authors to update their own comments
        - Logs update operations for audit purposes
    """
    try:
        response = comments_client.update_comment(
            comment_id, update_data.new_text
        )
        logger.info(
            f"User {current_user['email']} updated comment {comment_id}"
        )
        return {"comment_id": response.comment_id, "message": response.message}
    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.details()
            )
        logger.error(
            f"gRPC error in update_comment: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comments service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in update_comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int, current_user: dict = Depends(get_comment_author)
):
    """
    Delete a comment by its ID.

    Args:
        comment_id (int): The unique identifier of the comment to delete.
        current_user (dict): Authenticated user data from dependency (must be comment author).

    Returns:
        dict: Dictionary containing the deleted comment ID and status message.

    Raises:
        HTTPException:
            - 403: If user is not the comment author (handled by get_comment_author dependency)
            - 404: If comment with the specified ID is not found
            - 500: If comments service is unavailable or internal error occurs

    Note:
        - Only allows comment authors to delete their own comments
        - Logs deletion operations for audit purposes
        - Permanently removes the comment from the system
    """
    try:
        response = comments_client.delete_comment(comment_id)
        logger.info(
            f"User {current_user['email']} deleted comment {comment_id}"
        )
        return {"comment_id": response.comment_id, "message": response.message}
    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        logger.error(
            f"gRPC error in delete_comment: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comments service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in delete_comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
