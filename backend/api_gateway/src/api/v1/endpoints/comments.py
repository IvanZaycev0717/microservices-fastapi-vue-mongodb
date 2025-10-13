from fastapi import APIRouter, HTTPException, Depends
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
            status_code=500, detail="Comments service unavailable"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_all_comments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/comments/project/{project_id}")
async def get_comments_by_project_id(project_id: str):
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
            status_code=500, detail="Comments service unavailable"
        )
    except Exception as e:
        logger.exception(
            f"Unexpected error in get_comments_by_project_id: {e}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/comments/{comment_id}")
async def get_comment(comment_id: int):
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
            raise HTTPException(status_code=404, detail="Comment not found")
        logger.error(f"gRPC error in get_comment: {e.code()} - {e.details()}")
        raise HTTPException(
            status_code=500, detail="Comments service unavailable"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_comment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/comments")
async def create_comment(
    comment_data: CommentCreateRequest,
    current_user: dict = Depends(get_current_user),
):
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
            raise HTTPException(status_code=400, detail=e.details())
        logger.error(
            f"gRPC error in create_comment: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=500, detail="Comments service unavailable"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in create_comment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/comments/my")
async def get_my_comments(current_user: dict = Depends(get_current_user)):
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
            status_code=500, detail="Comments service unavailable"
        )
    except Exception as e:
        logger.exception(f"Unexpected error in get_my_comments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    update_data: CommentUpdateRequest,
    current_user: dict = Depends(get_comment_author)
):
    try:
        response = comments_client.update_comment(comment_id, update_data.new_text)
        logger.info(f"User {current_user['email']} updated comment {comment_id}")
        return {
            "comment_id": response.comment_id,
            "message": response.message
        }
    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Comment not found")
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(status_code=400, detail=e.details())
        logger.error(f"gRPC error in update_comment: {e.code()} - {e.details()}")
        raise HTTPException(status_code=500, detail="Comments service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in update_comment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: dict = Depends(get_comment_author)
):
    try:
        response = comments_client.delete_comment(comment_id)
        logger.info(f"User {current_user['email']} deleted comment {comment_id}")
        return {
            "comment_id": response.comment_id,
            "message": response.message
        }
    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Comment not found")
        logger.error(f"gRPC error in delete_comment: {e.code()} - {e.details()}")
        raise HTTPException(status_code=500, detail="Comments service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in delete_comment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
