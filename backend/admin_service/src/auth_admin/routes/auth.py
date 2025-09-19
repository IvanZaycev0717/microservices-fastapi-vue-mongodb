import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.asynchronous.database import AsyncDatabase

from auth_admin.crud.auth import AuthCRUD
from auth_admin.dependencies import (
    authenticate_user,
    get_current_active_user,
    get_db,
)
from auth_admin.models.auth import (
    CreateUserForm,
    Token,
    UserResponse,
    UserUpdateForm,
)
from content_admin.dependencies import get_logger_factory
from services.password_processor import get_password_hash
from services.token_processor import create_access_token
from settings import settings

router = APIRouter(prefix="/auth")


@router.get("", response_model=list[UserResponse])
async def get_all_users(
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.AUTH_ADMIN_NAME)),
    ],
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

        for user in users:
            user["id"] = str(user["_id"])
            del user["_id"]
            user.pop("password_hash", None)
            user.pop("_id", None)

        logger.info(f"Successfully retrieved {len(users)} users")
        return users

    except Exception as e:
        logger.exception(f"Failed to fetch users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching users",
        )


@router.post("/register", response_model=dict)
async def register_user(
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.AUTH_ADMIN_NAME)),
    ],
    user_data: Annotated[CreateUserForm, Form()],
    db: Annotated[AsyncDatabase, Depends(get_db)],
):
    """Register new user and return access token."""
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        auth_crud = AuthCRUD(db)

        # Check if user already exists
        existing_user = await auth_crud.get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(
                f"Registration failed - email already exists: {user_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Hash password
        hashed_password = get_password_hash(user_data.password)
        if not hashed_password:
            logger.error("Password hashing failed during registration")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

        # Create user
        user = await auth_crud.create_user(
            email=user_data.email,
            password_hash=hashed_password,
            roles=user_data.roles,
        )

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user["email"],
                "email": user["email"],
                "roles": user["roles"],
            }
        )

        logger.info(f"User registered successfully: {user_data.email}")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(user["_id"]),
        }

    except HTTPException:
        # Re-raise already handled HTTP exceptions
        raise

    except Exception as e:
        logger.exception(f"Registration failed for {user_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration",
        )


@router.post("/login", response_model=Token)
async def login_for_access_token(
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.AUTH_ADMIN_NAME)),
    ],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncDatabase, Depends(get_db)],
):
    """Login user and return access token."""
    try:
        logger.info(f"Login attempt for username: {form_data.username}")

        user = await authenticate_user(
            form_data.username, form_data.password, db
        )
        if not user:
            logger.warning(f"Failed login attempt for: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login time
        auth_crud = AuthCRUD(db)
        await auth_crud.update_user_last_login(form_data.username)

        access_token = create_access_token(
            data={
                "sub": user["email"],
                "email": user["email"],
                "roles": user.get("roles", []),
            }
        )

        logger.info(f"User logged in successfully: {form_data.username}")

        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        # Re-raise already handled HTTP exceptions
        raise

    except Exception as e:
        logger.exception(f"Login failed for {form_data.username}: {e}")
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

        # Remove sensitive data from response
        user_response = current_user.copy()
        user_response.pop("password_hash", None)
        user_response.pop("_id", None)

        # Ensure id field is present
        if "_id" in current_user:
            user_response["id"] = str(current_user["_id"])

        logger.info(
            f"User profile retrieved successfully for: {current_user.get('email')}"
        )

        return user_response

    except HTTPException:
        # Re-raise already handled HTTP exceptions from dependencies
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
    logger: Annotated[
        logging.Logger,
        Depends(get_logger_factory(settings.AUTH_ADMIN_NAME)),
    ],
    email: Annotated[str, Form(description="Email пользователя для удаления")],
    db=Depends(get_db),
):
    """Delete user by email address."""
    try:
        auth_crud = AuthCRUD(db)

        user = await auth_crud.get_user_by_email(email)
        if not user:
            logger.warning(f"Attempt to delete non-existent user: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        deleted = await auth_crud.delete_user_by_email(email)
        if not deleted:
            logger.error(f"Failed to delete user: {email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user",
            )

        logger.info(f"User deleted successfully: {email}")

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"Unexpected error during user deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
