from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    Cookie,
    Depends,
    status,
)
from grpc import RpcError
import grpc

from grpc_clients.auth_client import AuthClient
from logger import get_logger
from settings import settings
from api.v1.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    VerifyRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    LoginResponse,
    RegisterResponse,
    RefreshResponse,
    VerifyResponse,
    ForgotPasswordResponse,
    ResetPasswordResponse,
    LogoutResponse,
)
from api.v1.dependencies import get_current_user
from services.rate_limit_decorator import rate_limited
from services.dependencies import get_auth_token_bucket
from services.token_bucket import TokenBucket

router = APIRouter()
logger = get_logger("AuthEndpoints")
auth_client = AuthClient()


@router.post("/login", response_model=LoginResponse)
@rate_limited()
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    token_bucket: TokenBucket = Depends(get_auth_token_bucket),
):
    """
    Authenticate user and set refresh token as HTTP-only cookie.

    Args:
        response (Response): FastAPI response object for setting cookies.
        login_data (LoginRequest): Login credentials containing email and password.

    Returns:
        LoginResponse: Authentication tokens and user information.

    Raises:
        HTTPException:
            - 401: If authentication fails due to invalid credentials
            - 403: If user account is banned
            - 500: If auth service is unavailable or internal error occurs

    Note:
        - Sets refresh token as secure HTTP-only cookie for automatic token refresh
        - Returns access token in response body for API authorization
        - Converts gRPC errors to appropriate HTTP status codes
    """
    try:
        grpc_response = auth_client.login(
            login_data.email, login_data.password
        )

        response.set_cookie(
            key=settings.COOKIE_KEY,
            value=grpc_response.refresh_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=grpc_response.expires_in,
            path=settings.COOKIE_PATH,
        )

        return LoginResponse(
            access_token=grpc_response.access_token,
            token_type=grpc_response.token_type,
            expires_in=grpc_response.expires_in,
            user_id=grpc_response.user_id,
            user={
                "id": grpc_response.user.id,
                "email": grpc_response.user.email,
                "roles": list(grpc_response.user.roles),
                "is_banned": grpc_response.user.is_banned,
                "created_at": grpc_response.user.created_at,
                "last_login_at": grpc_response.user.last_login_at,
            },
        )
    except RpcError as e:
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            logger.warning(
                f"Login failed for {login_data.email}: Invalid credentials"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
            logger.warning(f"Login failed for {login_data.email}: User banned")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is banned",
            )
        else:
            logger.error(f"gRPC error in login: {e.code()} - {e.details()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Auth service unavailable",
            )
    except Exception as e:
        logger.exception(f"Unexpected error in login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/register", response_model=RegisterResponse)
@rate_limited()
async def register(
    request: Request,
    response: Response,
    register_data: RegisterRequest,
    token_bucket: TokenBucket = Depends(get_auth_token_bucket),
):
    """
    Register new user and set refresh token as HTTP-only cookie.

    Args:
        response (Response): FastAPI response object for setting cookies.
        register_data (RegisterRequest): Registration data containing email, password and optional roles.

    Returns:
        RegisterResponse: Authentication tokens and user information.

    Raises:
        HTTPException:
            - 400: If email format is invalid
            - 409: If user with email already exists
            - 500: If auth service is unavailable or internal error occurs

    Note:
        - Sets refresh token as secure HTTP-only cookie for automatic token refresh
        - Returns access token in response body for API authorization
        - Converts gRPC errors to appropriate HTTP status codes
    """
    try:
        grpc_response = auth_client.register(
            register_data.email, register_data.password, register_data.roles
        )

        response.set_cookie(
            key=settings.COOKIE_KEY,
            value=grpc_response.refresh_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=grpc_response.expires_in,
            path=settings.COOKIE_PATH,
        )

        return RegisterResponse(
            access_token=grpc_response.access_token,
            token_type=grpc_response.token_type,
            expires_in=grpc_response.expires_in,
            user_id=grpc_response.user_id,
            user={
                "id": grpc_response.user.id,
                "email": grpc_response.user.email,
                "roles": list(grpc_response.user.roles),
                "is_banned": grpc_response.user.is_banned,
                "created_at": grpc_response.user.created_at,
                "last_login_at": grpc_response.user.last_login_at,
            },
        )
    except RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            logger.warning(
                f"Registration failed: User already exists - {register_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            logger.warning(
                f"Registration failed: Invalid email - {register_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format",
            )
        else:
            logger.error(f"gRPC error in register: {e.code()} - {e.details()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Auth service unavailable",
            )
    except Exception as e:
        logger.exception(f"Unexpected error in register: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None, alias=settings.COOKIE_KEY),
):
    """
    Refresh authentication tokens using refresh token from cookie.

    Args:
        response (Response): FastAPI response object for setting new cookies.
        refresh_token (str): Refresh token extracted from HTTP-only cookie.

    Returns:
        RefreshResponse: New access token and token metadata.

    Raises:
        HTTPException:
            - 401: If refresh token is missing or invalid
            - 500: If auth service is unavailable or internal error occurs

    Note:
        - Extracts refresh token from HTTP-only cookie automatically
        - Sets new refresh token cookie with updated expiration
        - Returns new access token for continued API access
    """
    try:
        if not refresh_token:
            logger.warning("Refresh token missing in cookie")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token required",
            )

        logger.info("Token refresh requested")

        grpc_response = auth_client.refresh_token(refresh_token)

        response.set_cookie(
            key=settings.COOKIE_KEY,
            value=grpc_response.refresh_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=grpc_response.expires_in,
            path=settings.COOKIE_PATH,
        )

        logger.info("Tokens refreshed successfully")

        return RefreshResponse(
            access_token=grpc_response.access_token,
            token_type=grpc_response.token_type,
            expires_in=grpc_response.expires_in,
        )
    except RpcError as e:
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            logger.warning("Token refresh failed: Invalid refresh token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        else:
            logger.error(
                f"gRPC error in refresh_token: {e.code()} - {e.details()}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Auth service unavailable",
            )
    except Exception as e:
        logger.exception(f"Unexpected error in refresh_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    current_user: dict = Depends(get_current_user),
    refresh_token: str = Cookie(None),
):
    """
    Logout user by invalidating refresh token and removing cookie.

    Args:
        response (Response): FastAPI response object for cookie deletion.
        current_user (dict): Authenticated user data from dependency.
        refresh_token (str): Refresh token extracted from HTTP-only cookie.

    Returns:
        LogoutResponse: Empty response confirming logout operation.

    Raises:
        HTTPException:
            - 401: If user is not authenticated (handled by get_current_user dependency)

    Note:
        - Always deletes the refresh token cookie from client
        - Attempts to invalidate refresh token on server if present
        - Gracefully handles cases where refresh token is missing
        - Returns success even if gRPC call fails to ensure cookie cleanup
    """
    try:
        response.delete_cookie(
            key=settings.COOKIE_KEY,
            path=settings.COOKIE_PATH,
        )

        if refresh_token:
            auth_client.logout(refresh_token)
            logger.info(
                f"User logged out successfully: {current_user['email']}"
            )
        else:
            logger.warning(
                f"Logout called without refresh token by: {current_user['email']}"
            )

        return LogoutResponse()
    except RpcError as e:
        logger.error(f"gRPC error in logout: {e.code()} - {e.details()}")
        return LogoutResponse()
    except Exception as e:
        logger.exception(f"Unexpected error in logout: {e}")
        return LogoutResponse()


@router.post("/verify", response_model=VerifyResponse)
async def verify_token(verify_data: VerifyRequest):
    """
    Verify the validity of an authentication token.

    Args:
        verify_data (VerifyRequest): Request containing token to verify.

    Returns:
        VerifyResponse: Token verification result with user claims if valid.

    Raises:
        HTTPException:
            - 500: If auth service is unavailable or internal error occurs

    Note:
        - Returns detailed user information including roles if token is valid
        - Suitable for token validation from external services or frontend
    """
    try:
        grpc_response = auth_client.verify_token(verify_data.token)
        return VerifyResponse(
            valid=grpc_response.valid,
            user_id=grpc_response.user_id,
            email=grpc_response.email,
            roles=list(grpc_response.roles),
            error=grpc_response.error,
        )
    except RpcError as e:
        logger.error(f"gRPC error in verify_token: {e.code()} - {e.details()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in verify_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
@rate_limited()
async def forgot_password(
    request: Request,
    forgot_data: ForgotPasswordRequest,
    token_bucket: TokenBucket = Depends(get_auth_token_bucket),
):
    """
    Initiate password reset process for a user.

    Args:
        forgot_data (ForgotPasswordRequest): Request containing user's email.

    Returns:
        ForgotPasswordResponse: Password reset initiation result.

    Raises:
        HTTPException:
            - 500: If auth service is unavailable or internal error occurs

    Note:
        - Typically sends password reset instructions to the user's email
        - Returns success even for non-existent emails to prevent email enumeration
    """
    try:
        grpc_response = auth_client.forgot_password(forgot_data.email)
        return ForgotPasswordResponse(
            success=grpc_response.success,
            reset_token=grpc_response.reset_token,
            message=grpc_response.message,
        )
    except RpcError as e:
        logger.error(
            f"gRPC error in forgot_password: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in forgot_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/reset-password", response_model=ResetPasswordResponse)
@rate_limited()
async def reset_password(
    request: Request,
    reset_data: ResetPasswordRequest,
    token_bucket: TokenBucket = Depends(get_auth_token_bucket),
):
    """
    Reset user password using valid reset token.

    Args:
        reset_data (ResetPasswordRequest): Request containing reset token, new password and email.

    Returns:
        ResetPasswordResponse: Password reset operation result.

    Raises:
        HTTPException:
            - 500: If auth service is unavailable or internal error occurs

    Note:
        - Validates reset token and email combination for security
        - Logs both successful and failed password reset attempts
        - Updates user password if all validation checks pass
    """
    try:
        logger.info(f"Password reset attempt for: {reset_data.email}")

        grpc_response = auth_client.reset_password(
            reset_data.reset_token, reset_data.new_password, reset_data.email
        )

        if grpc_response.success:
            logger.info(f"Password reset successful for: {reset_data.email}")
        else:
            logger.warning(f"Password reset failed for: {reset_data.email}")

        return ResetPasswordResponse(
            success=grpc_response.success,
            message=grpc_response.message,
            user_id=grpc_response.user_id,
            email=grpc_response.email,
        )
    except RpcError as e:
        logger.error(
            f"gRPC error in reset_password: {e.code()} - {e.details()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth service unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in reset_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
