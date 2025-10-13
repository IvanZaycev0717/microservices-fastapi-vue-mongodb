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
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify JWT token and return current user data."""
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
            "roles": list(response.roles)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token verification",
        )


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Check if current user is active (not banned)."""
    # Note: We don't have is_banned info from VerifyToken response
    # This would need to be enhanced if we want to check banned status
    return current_user


async def get_comment_author(
    comment_id: int,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Verify that current user is the author of the comment."""
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
                detail="You can only modify your own comments"
            )
        
        return current_user
        
    except RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Comment not found")
        logger.error(f"gRPC error in comment author verification: {e.code()} - {e.details()}")
        raise HTTPException(status_code=500, detail="Comments service unavailable")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in comment author verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")