from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pymongo.asynchronous.database import AsyncDatabase

from services.password_processor import verify_password
from services.token_processor import verify_jwt_token


async def get_db(request: Request) -> AsyncDatabase:
    """Get async database instance from application state.

    Args:
        request: FastAPI Request object containing application state.

    Returns:
        AsyncDatabase: Async database instance for authentication admin.
    """
    return request.app.state.auth_admin_mongo_db


async def get_user(email: str, db: AsyncDatabase) -> dict | None:
    """Get user from database by email.

    Args:
        email (str): Email address to search for.
        db (AsyncDatabase): Async database instance.

    Returns:
        dict | None: User document if found, None otherwise.
    """
    return await db.users.find_one({"email": email})


async def authenticate_user(
    email: str, password: str, db: AsyncDatabase
) -> dict | None:
    """Authenticate user credentials against database.

    Args:
        email (str): User's email address.
        password (str): User's plain text password.
        db (AsyncDatabase): Async database instance.

    Returns:
        dict | None: User document if authentication successful, None otherwise.
    """
    user = await get_user(email, db)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncDatabase = Depends(get_db)
) -> dict:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    """Retrieve current user from JWT token.

    Args:
        token (str): JWT token from authorization header.
        db (AsyncDatabase): Async database instance.

    Returns:
        dict: Authenticated user data.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    try:
        payload = verify_jwt_token(token)
        email = payload.get("email")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = await get_user(email, db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Validate that current user is active and not banned.

    Args:
        current_user (dict): Authenticated user data from dependency.

    Returns:
        dict: User data if active and not banned.

    Raises:
        HTTPException: If user account is banned.
    """
    if current_user.get("is_banned"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is banned"
        )
    return current_user
