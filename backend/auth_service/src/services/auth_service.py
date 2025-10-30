from datetime import datetime, timedelta

import grpc
from grpc import ServicerContext
from jwt.exceptions import JWTException
from pydantic import ValidationError

from logger import get_logger
from models.schemas import (
    CreateUserRequest,
    ForgotPasswordRequest,
    LoginRequest,
)
from proto import auth_pb2, auth_pb2_grpc
from services.kafka_producer import (
    PasswordResetMessage,
    PasswordResetSuccessMessage,
    kafka_producer,
)
from services.password_processor import get_password_hash, verify_password
from services.token_processor import create_token_for_user, verify_jwt_token
from settings import settings

logger = get_logger("Service")


class AuthService(auth_pb2_grpc.AuthServiceServicer):
    """gRPC servicer implementation for authentication operations.

    Handles user authentication, token management, and related gRPC methods.

    Attributes:
        db_manager: Database manager instance for data access.
        auth_crud: CRUD operations for authentication data.
        token_crud: CRUD operations for token management.
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.auth_crud = db_manager.get_auth_crud()
        self.token_crud = db_manager.get_token_crud()

    async def Login(
        self, request: auth_pb2.LoginRequest, context: ServicerContext
    ) -> auth_pb2.LoginResponse:
        """Handles user login authentication and token generation.

        Processes login requests, validates credentials, and generates access
        and refresh tokens upon successful authentication.

        Args:
            request: LoginRequest containing email and password.
            context: gRPC servicer context for handling errors.

        Returns:
            auth_pb2.LoginResponse: Response containing authentication tokens
            and user information.

        Raises:
            grpc.aio.ServicerContext.abort:
                - UNAUTHENTICATED for invalid credentials
                - PERMISSION_DENIED for banned users
                - INTERNAL for server errors

        Note:
            - Validates user credentials against stored hash
            - Updates last login timestamp on successful authentication
            - Creates both access and refresh tokens with different expiration
            - Stores refresh token in database for future validation
        """
        try:
            logger.info(f"Login attempt for email: {request.email}")

            login_data = LoginRequest(
                email=request.email, password=request.password
            )

            user = await self.auth_crud.get_user_by_email(login_data.email)
            if not user:
                logger.warning(f"User not found: {login_data.email}")
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Invalid credentials"
                )

            if not verify_password(
                login_data.password.get_secret_value(), user.password_hash
            ):
                logger.warning(f"Invalid password for: {login_data.email}")
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Invalid credentials"
                )

            if user.is_banned:
                logger.warning(
                    f"Banned user login attempt: {login_data.email}"
                )
                await context.abort(
                    grpc.StatusCode.PERMISSION_DENIED, "User account is banned"
                )

            await self.auth_crud.update_user_last_login(user.email)

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
                token_type="refresh",
            )

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
        """Handles new user registration and account creation.

        Processes registration requests, validates input, creates new user account,
        and generates initial authentication tokens.

        Args:
            request: RegisterRequest containing email and password.
            context: gRPC servicer context for handling errors.

        Returns:
            auth_pb2.RegisterResponse: Response containing authentication tokens
            and user information for the newly created account.

        Raises:
            grpc.aio.ServicerContext.abort:
                - ALREADY_EXISTS if user with email already registered
                - INVALID_ARGUMENT for invalid email format
                - INTERNAL for server errors or password hashing failures

        Note:
            - Assigns default "user" role to new registrations
            - Validates email format using Pydantic validation
            - Creates both access and refresh tokens upon successful registration
            - Stores refresh token in database for session management
        """
        try:
            logger.info(f"Registration attempt for email: {request.email}")

            register_data = CreateUserRequest(
                email=request.email,
                password=request.password,
                roles=["user"],
            )

            existing_user = await self.auth_crud.get_user_by_email(
                register_data.email
            )
            if existing_user:
                logger.warning(f"User already exists: {register_data.email}")
                await context.abort(
                    grpc.StatusCode.ALREADY_EXISTS,
                    "User with this email already exists",
                )

            hashed_password = get_password_hash(
                register_data.password.get_secret_value()
            )
            if not hashed_password:
                logger.error("Password hashing failed")
                await context.abort(
                    grpc.StatusCode.INTERNAL, "Internal server error"
                )

            user = await self.auth_crud.create_user(
                email=register_data.email,
                password_hash=hashed_password,
                roles=register_data.roles,
            )

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
                token_type="refresh",
            )

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
        except ValidationError:
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, "Invalid email format"
            )

        except Exception as e:
            logger.exception(f"Registration failed for {request.email}: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )

    async def Logout(
        self, request: auth_pb2.LogoutRequest, context: ServicerContext
    ) -> auth_pb2.LogoutResponse:
        """Logout user by invalidating refresh token.

        Processes logout requests by marking the provided refresh token as used,
        preventing its future use for token refresh operations.

        Args:
            request: LogoutRequest containing the refresh token to invalidate.
            context: gRPC servicer context for handling errors.

        Returns:
            auth_pb2.LogoutResponse: Response indicating logout success status.

        Raises:
            grpc.aio.ServicerContext.abort:
                - INVALID_ARGUMENT if refresh token is not provided
                - INTERNAL for server errors during token invalidation

        Note:
            - Returns success even if token was already invalidated (security measure)
            - Only invalidates refresh tokens, access tokens remain valid until expiration
            - Prevents replay attacks by marking tokens as used in database
        """
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
        """Refreshes authentication tokens using a valid refresh token.

        Validates the provided refresh token and issues new access and refresh tokens
        if validation passes. Implements token rotation for enhanced security.

        Args:
            request: RefreshTokenRequest containing the refresh token.
            context: gRPC servicer context for handling errors.

        Returns:
            auth_pb2.RefreshTokenResponse: Response containing new access and refresh tokens.

        Raises:
            grpc.aio.ServicerContext.abort:
                - INVALID_ARGUMENT if refresh token is not provided
                - UNAUTHENTICATED for invalid, wrong type, or expired tokens
                - NOT_FOUND if user no longer exists
                - PERMISSION_DENIED if user is banned
                - INTERNAL for server errors

        Note:
            - Implements token rotation by issuing new refresh token and invalidating old one
            - Validates token type to ensure only refresh tokens are accepted
            - Checks token expiration and user status before issuing new tokens
            - Marks used refresh tokens as invalid to prevent reuse
        """
        try:
            if not request.refresh_token:
                await context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT,
                    "Refresh token is required",
                )

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

            stored_token = await self.token_crud.get_refresh_token(
                request.refresh_token
            )
            if not stored_token:
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    "Refresh token not found or already used",
                )

            if datetime.fromtimestamp(payload["exp"]) < datetime.now():
                await self.token_crud.mark_token_as_used(request.refresh_token)
                await context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Refresh token expired"
                )

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
                token_type="refresh",
            )

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
        """Verifies the validity of a JWT token and extracts user claims.

        Validates the token signature and expiration, then returns the decoded
        payload if the token is valid.

        Args:
            request: VerifyTokenRequest containing the token to verify.
            context: gRPC servicer context.

        Returns:
            auth_pb2.VerifyTokenResponse: Response indicating token validity
            and containing user claims if valid.

        Note:
            - Returns detailed error messages for different failure scenarios
            - Extracts user_id, email, and roles from valid token payload
            - Handles JWT exceptions gracefully without aborting the call
            - Logs verification failures for security monitoring
        """
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
        """Generate reset token for password recovery.

        Processes password reset requests by generating a time-limited reset token
        and sending it via Kafka message for email delivery.

        Args:
            request: ForgotPasswordRequest containing the user's email.
            context: gRPC servicer context for handling errors.

        Returns:
            auth_pb2.ForgotPasswordResponse: Response indicating success status
            and containing the reset token.

        Raises:
            grpc.aio.ServicerContext.abort: INTERNAL for server errors.

        Note:
            - Returns success even for non-existent emails as security measure
            - Generates reset token with specific type and shorter expiration
            - Sends reset token via Kafka for email delivery
            - Logs failures in message delivery but doesn't fail the request
        """
        try:
            forgot_data = ForgotPasswordRequest(email=request.email)

            user = await self.auth_crud.get_user_by_email(forgot_data.email)
            if not user:
                logger.info(
                    f"Password reset requested for non-existent email: {forgot_data.email}"
                )
                return auth_pb2.ForgotPasswordResponse(
                    success=True,
                    reset_token="",
                    message="If the email exists, a reset link will be sent",
                )

            reset_token = create_token_for_user(
                user_id=user.id,
                email=user.email,
                expires_delta=timedelta(
                    minutes=settings.RESET_PASSWORD_TOKEN_EXPIRE_MINUTES
                ),
                roles=user.roles,
                token_type="reset",
            )

            logger.info(f"Password reset token generated for: {user.email}")

            password_reset_msg = PasswordResetMessage(
                email=user.email, reset_token=reset_token, user_id=user.id
            )

            if not kafka_producer.send_password_reset(password_reset_msg):
                logger.error(
                    f"Failed to send password reset message for: {user.email}"
                )

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

    async def ResetPassword(
        self, request: auth_pb2.ResetPasswordRequest, context: ServicerContext
    ) -> auth_pb2.ResetPasswordResponse:
        """Reset password using reset token.

        Validates the reset token and updates the user's password if all
        checks pass. Sends notification upon successful password reset.

        Args:
            request: ResetPasswordRequest containing reset token, email, and new password.
            context: gRPC servicer context for handling errors.

        Returns:
            auth_pb2.ResetPasswordResponse: Response indicating success status
            with user information if successful.

        Raises:
            grpc.aio.ServicerContext.abort: INTERNAL for server errors.

        Note:
            - Validates reset token type and expiration
            - Ensures token email matches request email
            - Enforces minimum password length requirement
            - Sends success notification via Kafka after password update
            - Returns detailed error messages for different failure scenarios
        """
        try:
            try:
                payload = verify_jwt_token(request.reset_token)
            except JWTException:
                return auth_pb2.ResetPasswordResponse(
                    success=False, message="Invalid or expired reset token"
                )

            if payload.get("type") != "reset":
                return auth_pb2.ResetPasswordResponse(
                    success=False, message="Invalid token type"
                )

            if payload.get("email") != request.email:
                return auth_pb2.ResetPasswordResponse(
                    success=False, message="Email does not match reset token"
                )

            if len(request.new_password) < settings.MIN_PASSWORD_LENGTH:
                return auth_pb2.ResetPasswordResponse(
                    success=False,
                    message=f"Password must be at least {settings.MIN_PASSWORD_LENGTH} characters",
                )

            user_id = payload.get("user_id")
            hashed_password = get_password_hash(request.new_password)

            if not hashed_password:
                return auth_pb2.ResetPasswordResponse(
                    success=False, message="Password hashing failed"
                )

            success = await self.auth_crud.update_user_password(
                user_id, hashed_password
            )

            if not success:
                return auth_pb2.ResetPasswordResponse(
                    success=False, message="Failed to update password"
                )

            password_reset_success_msg = PasswordResetSuccessMessage(
                email=request.email, user_id=user_id
            )

            kafka_producer.send_password_reset_success(
                password_reset_success_msg
            )

            logger.info(
                f"Password successfully reset for user: {request.email}"
            )

            return auth_pb2.ResetPasswordResponse(
                success=True,
                message="Password successfully reset",
                user_id=user_id,
                email=request.email,
            )

        except Exception as e:
            logger.exception(f"Password reset failed: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, "Internal server error"
            )
