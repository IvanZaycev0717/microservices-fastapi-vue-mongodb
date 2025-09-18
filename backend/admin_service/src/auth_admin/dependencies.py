from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pymongo.asynchronous.database import AsyncDatabase

from services.password_processor import verify_password
from services.token_processor import verify_access_token


async def get_db(request: Request) -> AsyncDatabase:
    return request.app.state.auth_admin_mongo_db


async def get_user(email: str, db: AsyncDatabase) -> dict | None:
    """Get user from database by email."""
    return await db.users.find_one({"email": email})


async def authenticate_user(
    email: str, password: str, db: AsyncDatabase
) -> dict | None:
    """Authenticate user with email and password."""
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

    try:
        payload = verify_access_token(token)
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
    """Check if current user is active and not banned."""
    if current_user.get("is_banned"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is banned"
        )
    return current_user
