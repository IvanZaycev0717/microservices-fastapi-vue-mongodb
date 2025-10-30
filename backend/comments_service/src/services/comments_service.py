from datetime import datetime

import grpc
from grpc import ServicerContext

from crud.comments import CommentsCRUD
from logger import get_logger
from proto import comments_pb2, comments_pb2_grpc
from schemas import CreateCommentForm, UpdateCommentRequest
from services.database import get_db_session

logger = get_logger("gRPC")


class CommentsService(comments_pb2_grpc.CommentsServiceServicer):
    async def CreateComment(
        self,
        request: comments_pb2.CreateCommentRequest,
        context: ServicerContext,
    ):
        """Handles creation of new comments.

        Validates comment data, stores it in the database, and returns the created comment ID.

        Args:
            request: CreateCommentRequest containing comment details.
            context: gRPC servicer context for error handling.

        Returns:
            comments_pb2.CreateCommentResponse: Response containing the created comment ID.

        Note:
            - Sets default values for created_at, likes, and dislikes
            - Handles both top-level comments and replies to parent comments
            - Uses database transaction via context manager
            - Provides appropriate gRPC status codes for different error scenarios
        """
        logger.info(f"Create comment for project {request.project_id}")

        try:
            comment_form = CreateCommentForm(
                project_id=request.project_id,
                author_id=request.author_id,
                author_email=request.author_email,
                comment_text=request.comment_text,
                parent_comment_id=request.parent_comment_id
                if request.parent_comment_id
                else None,
            )

            comment_data = comment_form.model_dump()
            comment_data.update(
                {"created_at": datetime.now(), "likes": 0, "dislikes": 0}
            )

            async with get_db_session() as session:
                crud = CommentsCRUD(session)
                comment_id = await crud.create_comment(comment_data)

                return comments_pb2.CreateCommentResponse(
                    comment_id=comment_id,
                    message="Comment created successfully",
                )

        except ValueError as e:
            logger.error(f"Validation error creating comment: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return comments_pb2.CreateCommentResponse()
        except Exception as e:
            logger.error(f"Create comment error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.CreateCommentResponse()

    async def GetAllComments(
        self,
        request: comments_pb2.GetAllCommentsRequest,
        context: ServicerContext,
    ):
        """Retrieves all comments from the database.

        Fetches all available comments and converts them to protobuf format.

        Args:
            request: GetAllCommentsRequest (empty request).
            context: gRPC servicer context for error handling.

        Returns:
            comments_pb2.GetAllCommentsResponse: Response containing all comments.

        Note:
            - Returns comments in protobuf format
            - Handles database errors and converts to gRPC status codes
            - Returns empty list if no comments exist
        """
        logger.info("Get all comments")

        try:
            async with get_db_session() as session:
                crud = CommentsCRUD(session)
                comments = await crud.read_all_comments()

                comment_protos = [
                    self._comment_to_proto(comment) for comment in comments
                ]
                return comments_pb2.GetAllCommentsResponse(
                    comments=comment_protos
                )

        except Exception as e:
            logger.error(f"Get all comments error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.GetAllCommentsResponse()

    async def GetComment(
        self, request: comments_pb2.GetCommentRequest, context: ServicerContext
    ):
        """Retrieves a specific comment by its ID.

        Fetches a single comment from the database and returns it in protobuf format.

        Args:
            request: GetCommentRequest containing the comment ID.
            context: gRPC servicer context for error handling.

        Returns:
            comments_pb2.GetCommentResponse: Response containing the requested comment.

        Raises:
            ValueError: If comment with the specified ID is not found.

        Note:
            - Returns NOT_FOUND status if comment doesn't exist
            - Converts database comment to protobuf format
        """
        logger.info(f"Get comment {request.comment_id}")

        try:
            async with get_db_session() as session:
                crud = CommentsCRUD(session)
                comment = await crud.read_one_comment(request.comment_id)
                return comments_pb2.GetCommentResponse(
                    comment=self._comment_to_proto(comment)
                )

        except ValueError as e:
            logger.error(f"Comment not found: {e}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return comments_pb2.GetCommentResponse()
        except Exception as e:
            logger.error(f"Get comment error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.GetCommentResponse()

    async def GetCommentsByProjectId(
        self,
        request: comments_pb2.GetCommentsByProjectIdRequest,
        context: ServicerContext,
    ):
        """Retrieves all comments for a specific project.

        Fetches comments associated with a particular project ID and returns
        them in protobuf format.

        Args:
            request: GetCommentsByProjectIdRequest containing the project ID.
            context: gRPC servicer context for error handling.

        Returns:
            comments_pb2.GetCommentsByProjectIdResponse: Response containing
            all comments for the specified project.

        Note:
            - Returns NOT_FOUND status if no comments exist for the project
            - Returns empty list if project exists but has no comments
            - Converts database comments to protobuf format
        """
        logger.info(f"Get comments for project {request.project_id}")

        try:
            async with get_db_session() as session:
                crud = CommentsCRUD(session)
                comments = await crud.get_comments_by_project_id(
                    request.project_id
                )

                comment_protos = [
                    self._comment_to_proto(comment) for comment in comments
                ]
                return comments_pb2.GetCommentsByProjectIdResponse(
                    comments=comment_protos
                )

        except ValueError as e:
            logger.error(f"Project comments not found: {e}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return comments_pb2.GetCommentsByProjectIdResponse()
        except Exception as e:
            logger.error(f"Get project comments error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.GetCommentsByProjectIdResponse()

    async def GetCommentsByAuthorId(
        self,
        request: comments_pb2.GetCommentsByAuthorIdRequest,
        context: ServicerContext,
    ):
        """Retrieves all comments by a specific author.

        Fetches comments associated with a particular author ID and returns
        them in protobuf format.

        Args:
            request: GetCommentsByAuthorIdRequest containing the author ID.
            context: gRPC servicer context for error handling.

        Returns:
            comments_pb2.GetCommentsByAuthorIdResponse: Response containing
            all comments by the specified author.

        Note:
            - Returns NOT_FOUND status if no comments exist for the author
            - Returns empty list if author exists but has no comments
            - Converts database comments to protobuf format
        """
        logger.info(f"Get comments for author {request.author_id}")

        try:
            async with get_db_session() as session:
                crud = CommentsCRUD(session)
                comments = await crud.get_comments_by_author_id(
                    request.author_id
                )

                comment_protos = [
                    self._comment_to_proto(comment) for comment in comments
                ]
                return comments_pb2.GetCommentsByAuthorIdResponse(
                    comments=comment_protos
                )

        except ValueError as e:
            logger.error(f"Author comments not found: {e}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return comments_pb2.GetCommentsByAuthorIdResponse()
        except Exception as e:
            logger.error(f"Get author comments error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.GetCommentsByAuthorIdResponse()

    async def UpdateComment(
        self,
        request: comments_pb2.UpdateCommentRequest,
        context: ServicerContext,
    ):
        """Update comment text."""
        logger.info(f"Update comment {request.comment_id}")

        try:
            update_form = UpdateCommentRequest(new_text=request.new_text)

            async with get_db_session() as session:
                crud = CommentsCRUD(session)
                comment_id = await crud.update_comment(
                    request.comment_id, update_form.new_text
                )

                return comments_pb2.UpdateCommentResponse(
                    comment_id=comment_id,
                    message="Comment updated successfully",
                )

        except ValueError as e:
            logger.error(f"Validation error updating comment: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return comments_pb2.UpdateCommentResponse()
        except Exception as e:
            logger.error(f"Update comment error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.UpdateCommentResponse()

    async def DeleteComment(
        self,
        request: comments_pb2.DeleteCommentRequest,
        context: ServicerContext,
    ):
        """Deletes a comment by its ID.

        Removes a comment from the database and returns the deleted comment ID.

        Args:
            request: DeleteCommentRequest containing the comment ID to delete.
            context: gRPC servicer context for error handling.

        Returns:
            comments_pb2.DeleteCommentResponse: Response confirming deletion
            with the deleted comment ID.

        Note:
            - Returns NOT_FOUND status if comment doesn't exist
            - Cascades deletion to any child comments (replies)
            - Returns success message upon successful deletion
        """
        logger.info(f"Delete comment {request.comment_id}")

        try:
            async with get_db_session() as session:
                crud = CommentsCRUD(session)
                comment_id = await crud.delete_comment(request.comment_id)

                return comments_pb2.DeleteCommentResponse(
                    comment_id=comment_id,
                    message="Comment deleted successfully",
                )

        except ValueError as e:
            logger.error(f"Comment not found for delete: {e}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return comments_pb2.DeleteCommentResponse()
        except Exception as e:
            logger.error(f"Delete comment error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return comments_pb2.DeleteCommentResponse()

    def _comment_to_proto(self, comment):
        """Converts a database Comment object to protobuf format.

        Args:
            comment: The database Comment object to convert.

        Returns:
            comments_pb2.Comment: The converted comment in protobuf format.

        Note:
            - Converts datetime objects to ISO format strings
            - Handles None values for parent_comment_id by converting to 0
            - Preserves all comment attributes including engagement metrics
        """
        return comments_pb2.Comment(
            id=comment.id,
            project_id=comment.project_id,
            author_id=comment.author_id,
            author_email=comment.author_email,
            comment_text=comment.comment_text,
            created_at=comment.created_at.isoformat(),
            parent_comment_id=comment.parent_comment_id or 0,
            likes=comment.likes,
            dislikes=comment.dislikes,
        )
