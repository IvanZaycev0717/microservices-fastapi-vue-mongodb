from datetime import datetime, timedelta

import grpc
from grpc import ServicerContext
from jwt.exceptions import JWTException

from logger import get_logger
from models.schemas import (
    CreateUserRequest,
    ForgotPasswordRequest,
    LoginRequest,
)
from proto import auth_pb2, auth_pb2_grpc
from services.password_processor import get_password_hash, verify_password
from services.token_processor import create_token_for_user, verify_jwt_token
from settings import settings

logger = get_logger(f"{settings.GRPC_AUTH_NAME} - Service")


class AuthService(auth_pb2_grpc.AuthServiceServicer):
    """gRPC service for authentication operations."""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.auth_crud = db_manager.get_auth_crud()
        self.token_crud = db_manager.get_token_crud()

    async def Login(
        self, request: auth_pb2.LoginRequest, context: ServicerContext
    ) -> auth_pb2.LoginResponse:
        """Authenticate user and generate tokens."""
        try:
            logger.info(f"Login attempt for email: {request.email}")

            # Validate input using Pydantic
            login_data = LoginRequest(
                email=request.email, password=request.password
            )

            # Get user from database
            user = await self.auth_crud.get_user_by_email(login_data.email)
            if not user:
                logger.warning(f"User not found: {login_data.email}")
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Invalid credentials"
                )

            # Verify password
            if not verify_password(
                login_data.password.get_secret_value(), user.password_hash
            ):
                logger.warning(f"Invalid password for: {login_data.email}")
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Invalid credentials"
                )

            # Check if user is banned
            if user.is_banned:
                logger.warning(
                    f"Banned user login attempt: {login_data.email}"
                )
                await context.abort(
                    grpc.StatusCode.PERMISSION_DENIED, "User account is banned"
                )

            # Update last login
            await self.auth_crud.update_user_last_login(user.email)

            # Generate tokens
            access_token = create_token_for_user(
                user_id=user.id,
                email=user.email,
                expires_delta=timedelta(
                    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                ),
                roles=user.roles,
            )

            refresh_token = create_token_for_user(
                user_id=user.id,
                email=user.email,
                expires_delta=timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                ),
                roles=user.roles,
            )

            # Store refresh token
            refresh_expires = datetime.now() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
            await self.token_crud.create_refresh_token(
                user.id, refresh_token, refresh_expires
            )

            logger.info(f"User logged in successfully: {user.email}")

            return auth_pb2.LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user_id=user.id,
                expires_in=int(
                    timedelta(
                        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                    ).total_seconds()
                ),
                user=auth_pb2.User(
                    id=user.id,
                    email=user.email,
                    roles=user.roles,
                    is_banned=user.is_banned,
                    created_at=user.created_at.isoformat(),
                    last_login_at=user.last_login_at.isoformat()
                    if user.last_login_at
                    else "",
                ),
            )

        except Exception as e:
            logger.exception(f"Login failed for {request.email}: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )

    async def Register(
        self, request: auth_pb2.RegisterRequest, context: ServicerContext
    ) -> auth_pb2.RegisterResponse:
        """Register a new user."""
        try:
            logger.info(f"Registration attempt for email: {request.email}")

            # Validate input
            register_data = CreateUserRequest(
                email=request.email,
                password=request.password,
                roles=request.roles or ["user"],
            )

            # Check if user already exists
            existing_user = await self.auth_crud.get_user_by_email(
                register_data.email
            )
            if existing_user:
                logger.warning(f"User already exists: {register_data.email}")
                await context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    "User with this email already exists",
                )

            # Hash password
            hashed_password = get_password_hash(
                register_data.password.get_secret_value()
            )
            if not hashed_password:
                logger.error("Password hashing failed")
                await context.abort(
                    grpc.StatusCode.INTERNAL, "Internal server error"
                )

            # Create user
            user = await self.auth_crud.create_user(
                email=register_data.email,
                password_hash=hashed_password,
                roles=register_data.roles,
            )

            # Generate tokens
            access_token = create_token_for_user(
                user_id=user.id,
                email=user.email,
                expires_delta=timedelta(
                    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                ),
                roles=user.roles,
            )

            refresh_token = create_token_for_user(
                user_id=user.id,
                email=user.email,
                expires_delta=timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                ),
                roles=user.roles,
            )

            # Store refresh token
            refresh_expires = datetime.now() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
            await self.token_crud.create_refresh_token(
                user.id, refresh_token, refresh_expires
            )

            logger.info(f"User registered successfully: {user.email}")

            return auth_pb2.RegisterResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                user_id=user.id,
                expires_in=int(
                    timedelta(
                        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                    ).total_seconds()
                ),
                user=auth_pb2.User(
                    id=user.id,
                    email=user.email,
                    roles=user.roles,
                    is_banned=user.is_banned,
                    created_at=user.created_at.isoformat(),
                    last_login_at=user.last_login_at.isoformat()
                    if user.last_login_at
                    else "",
                ),
            )

        except Exception as e:
            logger.exception(f"Registration failed for {request.email}: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )

    async def Logout(
        self, request: auth_pb2.LogoutRequest, context: ServicerContext
    ) -> auth_pb2.LogoutResponse:
        """Logout user by invalidating refresh token."""
        try:
            if not request.refresh_token:
                await context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Refresh token is required",
                )

            success = await self.token_crud.mark_token_as_used(
                request.refresh_token
            )

            if success:
                logger.info("Refresh token invalidated successfully")
                return auth_pb2.LogoutResponse(
                    success=True, message="Logged out successfully"
                )
            else:
                logger.warning("Refresh token already used or not found")
                return auth_pb2.LogoutResponse(
                    success=True, message="Logged out successfully"
                )

        except Exception as e:
            logger.exception(f"Logout failed: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )

    async def RefreshToken(
        self, request: auth_pb2.RefreshTokenRequest, context: ServicerContext
    ) -> auth_pb2.RefreshTokenResponse:
        """Refresh access token using valid refresh token."""
        try:
            if not request.refresh_token:
                await context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Refresh token is required",
                )

            # Verify refresh token
            try:
                payload = verify_jwt_token(request.refresh_token)
            except JWTException:
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Invalid refresh token"
                )

            if payload.get("type") != "refresh":
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Invalid token type"
                )

            # Check if token exists in database and is not used
            stored_token = await self.token_crud.get_refresh_token(
                request.refresh_token
            )
            if not stored_token:
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    "Refresh token not found or already used",
                )

            # Check expiration
            if datetime.fromtimestamp(payload["exp"]) < datetime.now():
                await self.token_crud.mark_token_as_used(request.refresh_token)
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Refresh token expired"
                )

            # Get user
            user = await self.auth_crud.get_user_by_email(payload["email"])
            if not user:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND, "User not found"
                )

            if user.is_banned:
                await self.token_crud.mark_token_as_used(request.refresh_token)
                await context.abort(
                    grpc.StatusCode.PERMISSION_DENIED, "User is banned"
                )

            # Generate new tokens
            access_token = create_token_for_user(
                user_id=user.id,
                email=user.email,
                expires_delta=timedelta(
                    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                ),
                roles=user.roles,
            )

            refresh_token = create_token_for_user(
                user_id=user.id,
                email=user.email,
                expires_delta=timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                ),
                roles=user.roles,
            )

            # Store new refresh token and mark old as used
            refresh_expires = datetime.now() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
            await self.token_crud.create_refresh_token(
                user.id, refresh_token, refresh_expires
            )
            await self.token_crud.mark_token_as_used(request.refresh_token)

            logger.info(f"Tokens refreshed for user: {user.email}")

            return auth_pb2.RefreshTokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=int(
                    timedelta(
                        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                    ).total_seconds()
                ),
            )

        except Exception as e:
            logger.exception(f"Token refresh failed: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )

    async def VerifyToken(
        self, request: auth_pb2.VerifyTokenRequest, context: ServicerContext
    ) -> auth_pb2.VerifyTokenResponse:
        """Verify access token for API Gateway."""
        try:
            if not request.token:
                return auth_pb2.VerifyTokenResponse(
                    valid=False, error="Token is required"
                )

            try:
                payload = verify_jwt_token(request.token)

                return auth_pb2.VerifyTokenResponse(
                    valid=True,
                    user_id=payload.get("user_id", ""),
                    email=payload.get("email", ""),
                    roles=payload.get("roles", []),
                )

            except JWTException as e:
                logger.warning(f"Token verification failed: {e}")
                return auth_pb2.VerifyTokenResponse(
                    valid=False, error="Invalid token"
                )

        except Exception as e:
            logger.exception(f"Token verification error: {e}")
            return auth_pb2.VerifyTokenResponse(
                valid=False, error="Internal server error"
            )

    async def ForgotPassword(
        self, request: auth_pb2.ForgotPasswordRequest, context: ServicerContext
    ) -> auth_pb2.ForgotPasswordResponse:
        """Generate reset token for password recovery."""
        try:
            # Validate input
            forgot_data = ForgotPasswordRequest(email=request.email)

            # Check if user exists
            user = await self.auth_crud.get_user_by_email(forgot_data.email)
            if not user:
                # Return success even if user doesn't exist for security
                logger.info(
                    f"Password reset requested for non-existent email: {forgot_data.email}"
                )
                return auth_pb2.ForgotPasswordResponse(
                    success=True,
                    reset_token="",
                    message="If the email exists, a reset link will be sent",
                )

            # Generate reset token (short-lived)
            reset_token = create_token_for_user(
                user_id=user.id,
                email=user.email,
                expires_delta=timedelta(minutes=15),  # 15 minutes for reset
                roles=user.roles,
            )

            logger.info(f"Password reset token generated for: {user.email}")

            # In production, this token would be sent to Notification Service via message broker
            return auth_pb2.ForgotPasswordResponse(
                success=True,
                reset_token=reset_token,
                message="Reset token generated successfully",
            )

        except Exception as e:
            logger.exception(
                f"Forgot password failed for {request.email}: {e}"
            )
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )
