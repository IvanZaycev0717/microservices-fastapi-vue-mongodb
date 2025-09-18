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
async def get_all_users(db=Depends(get_db)):
    """Get all users (admin only)."""
    auth_crud = AuthCRUD(db)
    users = await auth_crud.get_all_users()

    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return users


@router.post("/register", response_model=dict)
async def register_user(
    user_data: Annotated[CreateUserForm, Form()], db=Depends(get_db)
):
    """Register new user and return access token."""
    auth_crud = AuthCRUD(db)

    existing_user = await auth_crud.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed_password = get_password_hash(user_data.password)

    user = await auth_crud.create_user(
        email=user_data.email,
        password_hash=hashed_password,
        roles=user_data.roles,
    )

    access_token = create_access_token(
        data={
            "sub": user["email"],
            "email": user["email"],
            "roles": user["roles"],
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user["_id"]),
    }


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncDatabase, Depends(get_db)],
):
    """Login user and return access token."""
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub": user["email"],
            "email": user["email"],
            "roles": user.get("roles", []),
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


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
