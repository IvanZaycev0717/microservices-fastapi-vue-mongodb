from fastapi import APIRouter, HTTPException, Response, Cookie, Depends
from grpc import RpcError

from grpc_clients.auth_client import AuthClient
from logger import get_logger
from settings import settings
from api.v1.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
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

router = APIRouter()
logger = get_logger("AuthEndpoints")
auth_client = AuthClient()


@router.post("/login", response_model=LoginResponse)
async def login(response: Response, login_data: LoginRequest):
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
        if e.code() == e.UNAUTHENTICATED:
            logger.warning(
                f"Login failed for {login_data.email}: Invalid credentials"
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")
        elif e.code() == e.PERMISSION_DENIED:
            logger.warning(f"Login failed for {login_data.email}: User banned")
            raise HTTPException(
                status_code=403, detail="User account is banned"
            )
        else:
            logger.error(f"gRPC error in login: {e.code()} - {e.details()}")
            raise HTTPException(
                status_code=500, detail="Auth service unavailable"
            )
    except Exception as e:
        logger.exception(f"Unexpected error in login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/register", response_model=RegisterResponse)
async def register(response: Response, register_data: RegisterRequest):
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
        if e.code() == e.ALREADY_EXISTS:
            logger.warning(
                f"Registration failed: User already exists - {register_data.email}"
            )
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
        elif e.code() == e.INVALID_ARGUMENT:
            logger.warning(
                f"Registration failed: Invalid email - {register_data.email}"
            )
            raise HTTPException(status_code=400, detail="Invalid email format")
        else:
            logger.error(f"gRPC error in register: {e.code()} - {e.details()}")
            raise HTTPException(
                status_code=500, detail="Auth service unavailable"
            )
    except Exception as e:
        logger.exception(f"Unexpected error in register: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    response: Response,
    current_user: dict = Depends(get_current_user),
    refresh_data: RefreshRequest = None,
    refresh_token: str = Cookie(None),
):
    try:
        logger.info(f"Token refresh requested by: {current_user['email']}")

        token_to_refresh = refresh_token or (
            refresh_data.refresh_token if refresh_data else None
        )

        if not token_to_refresh:
            logger.warning(
                f"Refresh token missing for user: {current_user['email']}"
            )
            raise HTTPException(
                status_code=401, detail="Refresh token required"
            )

        grpc_response = auth_client.refresh_token(token_to_refresh)

        response.set_cookie(
            key=settings.COOKIE_KEY,
            value=grpc_response.refresh_token,
            httponly=settings.COOKIE_HTTPONLY,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            max_age=grpc_response.expires_in,
            path=settings.COOKIE_PATH,
        )

        logger.info(
            f"Tokens refreshed successfully for: {current_user['email']}"
        )

        return RefreshResponse(
            access_token=grpc_response.access_token,
            token_type=grpc_response.token_type,
            expires_in=grpc_response.expires_in,
        )
    except RpcError as e:
        if e.code() == e.UNAUTHENTICATED:
            logger.warning(
                f"Token refresh failed for {current_user['email']}: Invalid refresh token"
            )
            raise HTTPException(
                status_code=401, detail="Invalid refresh token"
            )
        else:
            logger.error(
                f"gRPC error in refresh_token: {e.code()} - {e.details()}"
            )
            raise HTTPException(
                status_code=500, detail="Auth service unavailable"
            )
    except Exception as e:
        logger.exception(f"Unexpected error in refresh_token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    current_user: dict = Depends(get_current_user),  # Добавляем защиту
    refresh_token: str = Cookie(None),
):
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
        raise HTTPException(status_code=500, detail="Auth service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in verify_token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(forgot_data: ForgotPasswordRequest):
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
        raise HTTPException(status_code=500, detail="Auth service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in forgot_password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(reset_data: ResetPasswordRequest):
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
        raise HTTPException(status_code=500, detail="Auth service unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in reset_password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
