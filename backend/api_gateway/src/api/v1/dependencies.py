from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from grpc import RpcError
import grpc

from grpc_clients.auth_client import AuthClient
from grpc_clients.comments_client import CommentsClient
from logger import get_logger

security = HTTPBearer()
logger = get_logger("AuthDependencies")
auth_client = AuthClient()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Extracts and verifies JWT token to get current user information.

    Validates the bearer token from Authorization header and extracts
    user claims from the verified token payload.

    Args:
        credentials: HTTP authorization credentials containing the bearer token.

    Returns:
        dict: User information dictionary containing:
            - user_id: Unique identifier of the authenticated user
            - email: User's email address
            - roles: List of user's roles

    Raises:
        HTTPException: 401 Unauthorized for invalid or expired tokens.
        HTTPException: 500 Internal Server Error for token verification failures.

    Note:
        - Relies on external auth service for token validation
        - Converts roles set to list for JSON serialization
        - Includes WWW-Authenticate header in 401 responses
    """
    try:
        token = credentials.credentials
        response = auth_client.verify_token(token)

        if not response.valid:
            logger.warning("Invalid token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": response.user_id,
            "email": response.email,
            "roles": list(response.roles),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token verification",
        )


async def get_comment_author(
    comment_id: int,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Verifies that the current user is the author of the specified comment.

    Checks comment ownership by comparing current user ID with comment author ID
    retrieved from the comments service via gRPC.

    Args:
        comment_id: Integer ID of the comment to verify ownership for.
        current_user: Authenticated user information from token verification.

    Returns:
        dict: The current_user dictionary if ownership is verified.

    Raises:
        HTTPException: 403 Forbidden if user is not the comment author.
        HTTPException: 404 Not Found if the comment doesn't exist.
        HTTPException: 500 Internal Server Error for service or unexpected errors.

    Note:
        - Uses gRPC client to communicate with comments service
        - Handles specific gRPC error codes with appropriate HTTP status codes
        - Logs authorization attempts for security monitoring
    """
    try:
        comments_client = CommentsClient()
        response = comments_client.get_comment(comment_id)
        comment = response.comment

        if comment.author_id != current_user["user_id"]:
            logger.warning(
                f"User {current_user['email']} attempted to modify comment {comment_id} "
                f"owned by {comment.author_email}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify your own comments",
            )

        return current_user

    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        logger.error(
            f"gRPC error in comment author verification: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Comments service unavailable",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Unexpected error in comment author verification: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
