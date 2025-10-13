import grpc
from datetime import datetime
from grpc import ServicerContext

from crud.comments import CommentsCRUD
from logger import get_logger
from proto import comments_pb2, comments_pb2_grpc
from schemas import CreateCommentForm, UpdateCommentRequest
from services.database import get_db_session
from settings import settings

logger = get_logger(f"{settings.GRPC_COMMENTS_SERVICE_NAME} - gRPC")


class CommentsService(comments_pb2_grpc.CommentsServiceServicer):
    async def CreateComment(
        self,
        request: comments_pb2.CreateCommentRequest,
        context: ServicerContext,
    ):
        """Create a new comment."""
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

            # Prepare data for database
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
        """Get all comments."""
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
        """Get a specific comment by ID."""
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
        """Get comments by project ID."""
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
        """Get comments by author ID."""
        logger.info(f"Get comments for author {request.author_id}")

        try:
            async with get_db_session() as session:
                crud = CommentsCRUD(session)
                comments = await crud.get_comments_by_author_id(request.author_id)

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
        """Delete a comment."""
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
        """Convert SQLAlchemy Comment to protobuf Comment."""
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
