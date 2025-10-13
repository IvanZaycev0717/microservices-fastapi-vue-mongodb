import grpc
from protos.comments_service_pb2 import (
    CreateCommentRequest,
    GetAllCommentsRequest,
    GetCommentRequest,
    GetCommentsByProjectIdRequest,
    GetCommentsByAuthorIdRequest,
    UpdateCommentRequest,
    DeleteCommentRequest,
)
from protos.comments_service_pb2_grpc import CommentsServiceStub
from settings import settings
from logger import get_logger

logger = get_logger("CommentsClient")


class CommentsClient:
    def __init__(self):
        self.channel = grpc.insecure_channel(
            f"{settings.API_GATEWAY_COMMENTS_HOST}:{settings.GRPC_COMMENTS_PORT}"
        )
        self.stub = CommentsServiceStub(self.channel)
        logger.info("CommentsClient initialized")

    def create_comment(
        self,
        project_id: str,
        author_id: str,
        author_email: str,
        comment_text: str,
        parent_comment_id: int = None,
    ):
        try:
            logger.info(
                f"Creating comment for project {project_id} by {author_email}"
            )
            request = CreateCommentRequest(
                project_id=project_id,
                author_id=author_id,
                author_email=author_email,
                comment_text=comment_text,
                parent_comment_id=parent_comment_id or 0,
            )
            response = self.stub.CreateComment(request)
            logger.info(
                f"Comment created successfully with ID: {response.comment_id}"
            )
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in create_comment: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in create_comment: {e}")
            raise

    def get_all_comments(self):
        try:
            logger.info("Getting all comments")
            request = GetAllCommentsRequest()
            response = self.stub.GetAllComments(request)
            logger.info(f"Retrieved {len(response.comments)} comments")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in get_all_comments: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in get_all_comments: {e}")
            raise

    def get_comment(self, comment_id: int):
        try:
            logger.info(f"Getting comment {comment_id}")
            request = GetCommentRequest(comment_id=comment_id)
            response = self.stub.GetComment(request)
            logger.info(f"Retrieved comment {comment_id}")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in get_comment: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in get_comment: {e}")
            raise

    def get_comments_by_project_id(self, project_id: str):
        try:
            logger.info(f"Getting comments for project {project_id}")
            request = GetCommentsByProjectIdRequest(project_id=project_id)
            response = self.stub.GetCommentsByProjectId(request)
            logger.info(
                f"Retrieved {len(response.comments)} comments for project {project_id}"
            )
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in get_comments_by_project_id: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"Unexpected error in get_comments_by_project_id: {e}"
            )
            raise

    def get_comments_by_author_id(self, author_id: str):
        try:
            logger.info(f"Getting comments for author {author_id}")
            request = GetCommentsByAuthorIdRequest(author_id=author_id)
            response = self.stub.GetCommentsByAuthorId(request)
            logger.info(
                f"Retrieved {len(response.comments)} comments for author {author_id}"
            )
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in get_comments_by_author_id: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"Unexpected error in get_comments_by_author_id: {e}"
            )
            raise

    def update_comment(self, comment_id: int, new_text: str):
        try:
            logger.info(f"Updating comment {comment_id}")
            request = UpdateCommentRequest(
                comment_id=comment_id, new_text=new_text
            )
            response = self.stub.UpdateComment(request)
            logger.info(f"Comment {comment_id} updated successfully")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in update_comment: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in update_comment: {e}")
            raise

    def delete_comment(self, comment_id: int):
        try:
            logger.info(f"Deleting comment {comment_id}")
            request = DeleteCommentRequest(comment_id=comment_id)
            response = self.stub.DeleteComment(request)
            logger.info(f"Comment {comment_id} deleted successfully")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in delete_comment: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in delete_comment: {e}")
            raise
