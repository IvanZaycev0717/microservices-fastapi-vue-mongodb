from datetime import datetime, timezone
import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import JWTException
from pymongo.asynchronous.database import AsyncDatabase

from auth_admin.crud.auth import AuthCRUD
from auth_admin.dependencies import (
    authenticate_user,
    get_current_active_user,
    get_db,
)
from auth_admin.models.auth import (
    CreateUserForm,
    LoginForm,
    UserDB,
    UserResponse,
    UserUpdateForm,
)
from content_admin.dependencies import get_logger_factory
from services.password_processor import get_password_hash
from services.token_processor import create_jwt_token, verify_jwt_token
from settings import settings
from auth_admin.crud.token import TokenCRUD

router = APIRouter(prefix="/auth")


@router.get("", response_model=list[UserResponse])
async def get_all_users(
    logger: Annotated[logging.Logger, Depends(get_logger_factory(settings.AUTH_ADMIN_NAME))],
    db: Annotated[AsyncDatabase, Depends(get_db)],
):
    """Get all users (admin only)."""
    try:
        logger.info("Fetching all users")
        auth_crud = AuthCRUD(db)
        users = await auth_crud.get_all_users()

        if not users:
            logger.info("No users found in database")
            return []

        user_responses = []
        for user in users:
            user_response = UserResponse(
                id=user.id,
                email=user.email,
                is_banned=user.is_banned,
                roles=user.roles,
                created_at=user.created_at,
                last_login_at=user.last_login_at
            )
            user_responses.append(user_response)

        logger.info(f"Successfully retrieved {len(user_responses)} users")
        return user_responses

    except Exception as e:
        logger.exception(f"Failed to fetch users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching users",
        )

@router.post("/register", response_model=dict)
async def register_user(
    logger: Annotated[logging.Logger, Depends(get_logger_factory(settings.AUTH_ADMIN_NAME))],
    user_data: Annotated[CreateUserForm, Form()],
    db: Annotated[AsyncDatabase, Depends(get_db)],
):
    """Register new user and return access token with refresh token."""
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        auth_crud = AuthCRUD(db)
        token_crud = TokenCRUD(db)

        existing_user = await auth_crud.get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(f"Registration failed - email already exists: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        hashed_password = get_password_hash(user_data.password)
        if not hashed_password:
            logger.exception("Password hashing failed during registration")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

        user = await auth_crud.create_user(
            email=user_data.email,
            password_hash=hashed_password,
            roles=user_data.roles,
        )

        token_data = {
            "sub": user.email,
            "email": user.email,
            "roles": user.roles,
            "user_id": user.id,
        }

        access_token = create_jwt_token(
            data=token_data, expires_delta=settings.ACCESS_TOKEN_EXPIRE_AT
        )

        refresh_token_data = token_data.copy()
        refresh_token_data["type"] = "refresh"

        refresh_token = create_jwt_token(
            data=refresh_token_data,
            expires_delta=settings.REFRESH_TOKEN_EXPIRES_AT,
        )

        refresh_token_expires = (
            datetime.now() + settings.REFRESH_TOKEN_EXPIRES_AT
        )
        await token_crud.create_refresh_token(
            user_id=user.id,
            token=refresh_token,
            expired_at=refresh_token_expires,
        )

        logger.info(f"User registered successfully: {user_data.email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_AT.total_seconds(),
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Registration failed for {user_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration",
        )


@router.post("/login", response_model=dict)
async def login_for_access_token(
    logger: Annotated[logging.Logger, Depends(get_logger_factory(settings.AUTH_ADMIN_NAME))],
    form_data: Annotated[LoginForm, Depends()],
    db: Annotated[AsyncDatabase, Depends(get_db)],
):
    """Login user and return access token with refresh token."""
    try:
        logger.info(f"Login attempt for username: {form_data.email}")
        user_dict = await authenticate_user(form_data.email, form_data.password.get_secret_value(), db)
        if not user_dict:
            logger.warning(f"Failed login attempt for: {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            user_dict["id"] = str(user_dict["_id"])
            del user_dict["_id"]
            user = UserDB(**user_dict)

        if user.is_banned:
            logger.warning(f"Login attempt for banned user: {form_data.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is banned",
            )

        auth_crud = AuthCRUD(db)
        await auth_crud.update_user_last_login(form_data.email)

        token_data = {
            "sub": user.email,
            "email": user.email,
            "roles": user.roles,
            "user_id": user.id,
        }

        access_token = create_jwt_token(
            data=token_data, expires_delta=settings.ACCESS_TOKEN_EXPIRE_AT
        )

        refresh_token_data = token_data.copy()
        refresh_token_data["type"] = "refresh"

        refresh_token = create_jwt_token(
            data=refresh_token_data,
            expires_delta=settings.REFRESH_TOKEN_EXPIRES_AT,
        )

        token_crud = TokenCRUD(db)
        refresh_token_expires = (
            datetime.now(timezone.utc) + settings.REFRESH_TOKEN_EXPIRES_AT
        )

        await token_crud.create_refresh_token(
            user_id=user.id,
            token=refresh_token,
            expired_at=refresh_token_expires,
        )

        logger.info(f"User logged in successfully: {form_data.email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_AT.total_seconds(),
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Login failed for {form_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.AUTH_ADMIN_NAME)),
    ],
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """Get current user information."""
    try:
        logger.info(f"Fetching user profile for: {current_user.get('email')}")

        user_response = current_user.copy()
        user_response.pop("password_hash", None)
        user_response.pop("_id", None)

        if "_id" in current_user:
            user_response["id"] = str(current_user["_id"])

        logger.info(
            f"User profile retrieved successfully for: {current_user.get('email')}"
        )

        return user_response

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(
            f"Failed to fetch user profile for {current_user.get('email')}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching user profile",
        )


@router.patch("/update/{email}", response_model=dict)
async def update_user(
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.AUTH_ADMIN_NAME)),
    ],
    email: str,
    update_data: Annotated[UserUpdateForm, Form()],
    db: Annotated[AsyncDatabase, Depends(get_db)],
):
    """Update user fields (is_banned, roles)."""
    try:
        auth_crud = AuthCRUD(db)

        user = await auth_crud.get_user_by_email(email)
        if not user:
            logger.warning(f"Attempt to update non-existent user: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        update_dict = {}
        if update_data.is_banned is not None:
            update_dict["is_banned"] = update_data.is_banned
        if update_data.roles is not None:
            update_dict["roles"] = [role.value for role in update_data.roles]

        updated_user = await auth_crud.update_user(email, update_dict)
        if not updated_user:
            logger.error(f"Failed to update user: {email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user",
            )

        logger.info(f"User updated successfully: {email}")
        return {
            "message": "User updated successfully",
            "email": email,
            "updated_fields": list(update_dict.keys()),
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Unexpected error during user update: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_email(
    logger: Annotated[logging.Logger, Depends(get_logger_factory(settings.AUTH_ADMIN_NAME))],
    email: Annotated[str, Form(description="Email пользователя для удаления")],
    db=Depends(get_db),
):
    try:
        auth_crud = AuthCRUD(db)
        token_crud = TokenCRUD(db)

        user = await auth_crud.get_user_by_email(email)
        if not user:
            logger.warning(f"Attempt to delete non-existent user: {email}")
            raise HTTPException(status_code=404, detail="User not found")

        await token_crud.collection.delete_many({"user_id": user.id})

        deleted = await auth_crud.delete_user_by_email(email)
        if not deleted:
            logger.error(f"Failed to delete user: {email}")
            raise HTTPException(status_code=500, detail="Failed to delete user")

        logger.info(f"User and tokens deleted successfully: {email}")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error during user deletion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh", response_model=dict)
async def refresh_tokens(
    db: Annotated[AsyncDatabase, Depends(get_db)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.AUTH_ADMIN_NAME)),
    ],
    refresh_token: str = Body(embed=True),
):
    """Refresh access token using refresh token."""
    try:
        auth_crud = AuthCRUD(db)
        token_crud = TokenCRUD(db)

        try:
            payload = verify_jwt_token(
                refresh_token
            )
        except JWTException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        stored_token = await token_crud.get_refresh_token(refresh_token)
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or already used",
            )

        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            await token_crud.mark_token_as_used(refresh_token)
            raise HTTPException(401, detail="Refresh token expired")

        if stored_token["expired_at"] < datetime.now():
            await token_crud.mark_token_as_used(refresh_token)
            raise HTTPException(401, detail="Refresh token expired")

        user = await auth_crud.get_user_by_email(payload["email"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.is_banned:
            await token_crud.mark_token_as_used(refresh_token)
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail="User is banned"
            )

        token_data = {
            "sub": user.email,
            "email": user.email,
            "roles": user.roles,
            "user_id": user.id,
        }

        access_token = create_jwt_token(
            data=token_data, expires_delta=settings.ACCESS_TOKEN_EXPIRE_AT
        )

        await token_crud.mark_token_as_used(refresh_token)

        logger.info(f"Tokens refreshed successfully for user: {user.email}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_AT.total_seconds(),
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh",
        )


@router.post("/logout", response_model=dict)
async def logout(
    db: Annotated[AsyncDatabase, Depends(get_db)],
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.AUTH_ADMIN_NAME)),
    ],
    refresh_token: str = Body(embed=True),
):
    """Invalidate refresh token on logout."""
    try:
        token_crud = TokenCRUD(db)

        success = await token_crud.mark_token_as_used(refresh_token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token",
            )

        logger.info("User logged out successfully")
        return {"message": "Logged out successfully"}

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout",
        )
