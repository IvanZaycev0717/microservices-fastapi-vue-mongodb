from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from grpc_clients.auth_client import AuthClient
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