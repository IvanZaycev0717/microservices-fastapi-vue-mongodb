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
    """
    gRPC client for comments service.

    This class establishes an insecure gRPC channel to the comments service
    and creates a stub for making RPC calls related to comments operations.

    Attributes:
        channel: gRPC insecure channel to the comments service
        stub: CommentsServiceStub instance for making gRPC calls to comments service

    Note:
        - Uses insecure channel (no SSL/TLS) for connection
        - Connection details are taken from application settings for comments service
    """

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
        """
        Create a new comment for a project.

        Args:
            project_id (str): ID of the project to which the comment belongs.
            author_id (str): ID of the user creating the comment.
            author_email (str): Email of the user creating the comment.
            comment_text (str): The content of the comment.
            parent_comment_id (int, optional): ID of the parent comment if this is a reply.
                                              Defaults to None for top-level comments.

        Returns:
            CreateCommentResponse: gRPC response containing the created comment data.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during comment creation.

        Note:
            - Logs comment creation attempts and successful operations for monitoring
            - Parent comment ID of 0 indicates no parent (top-level comment)
        """
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
        """
        Retrieve all comments from the system.

        Returns:
            GetAllCommentsResponse: gRPC response containing a list of all comments.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during comments retrieval.

        Note:
            - Logs the retrieval operation and the number of comments returned
            - This method returns all comments regardless of project or hierarchy
        """
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
        """
        Retrieve a specific comment by its ID.

        Args:
            comment_id (int): The unique identifier of the comment to retrieve.

        Returns:
            GetCommentResponse: gRPC response containing the comment data.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during comment retrieval.

        Note:
            - Logs the comment retrieval operation for monitoring
            - Returns detailed information about the specified comment
        """
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
        """
        Retrieve all comments for a specific project.

        Args:
            project_id (str): The ID of the project to retrieve comments for.

        Returns:
            GetCommentsByProjectIdResponse: gRPC response containing comments for the project.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during comments retrieval.

        Note:
            - Logs the retrieval operation and the number of comments returned
            - Returns all comments associated with the specified project ID
        """
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
        """
        Update the text of an existing comment.

        Args:
            comment_id (int): The unique identifier of the comment to update.
            new_text (str): The new text content for the comment.

        Returns:
            UpdateCommentResponse: gRPC response containing the updated comment data.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during comment update.

        Note:
            - Logs the comment update operation for monitoring
            - Only updates the comment text, other fields remain unchanged
        """
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
        """
        Delete a comment by its ID.

        Args:
            comment_id (int): The unique identifier of the comment to delete.

        Returns:
            DeleteCommentResponse: gRPC response confirming the deletion operation.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during comment deletion.

        Note:
            - Logs the comment deletion operation for monitoring
            - Permanently removes the comment from the system
        """
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
