import grpc
from protos.auth_service_pb2 import (
    LoginRequest,
    RegisterRequest,
    LogoutRequest,
    RefreshTokenRequest,
    VerifyTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from protos.auth_service_pb2_grpc import AuthServiceStub
from settings import settings
from logger import get_logger

logger = get_logger("AuthClient")


class AuthClient:
    """
    gRPC client for authentication service.

    This class establishes an insecure gRPC channel to the authentication service
    and creates a stub for making RPC calls.

    Attributes:
        channel: gRPC insecure channel to the authentication service
        stub: AuthServiceStub instance for making gRPC calls to auth service

    Note:
        - Uses insecure channel (no SSL/TLS) for connection
        - Connection details are taken from application settings
    """

    def __init__(self):
        self.channel = grpc.insecure_channel(
            f"{settings.API_GATEWAY_AUTH_HOST}:{settings.GRPC_AUTH_PORT}"
        )
        self.stub = AuthServiceStub(self.channel)
        logger.info("AuthClient initialized")

    def login(self, email: str, password: str):
        """
        Authenticate user with email and password.

        Args:
            email (str): User's email address for authentication.
            password (str): User's password for authentication.

        Returns:
            LoginResponse: gRPC response containing authentication tokens and user data.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during authentication.

        Note:
            - Logs login attempts and successful authentications for monitoring
            - Raises exceptions to be handled by the calling code
        """
        try:
            logger.info(f"Login attempt for: {email}")
            request = LoginRequest(email=email, password=password)
            response = self.stub.Login(request)
            logger.info(f"Login successful for: {email}")
            return response
        except grpc.RpcError as e:
            logger.error(f"gRPC error in login: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in login: {e}")
            raise

    def register(self, email: str, password: str, roles: list[str] = None):
        """
        Register a new user with email, password and optional roles.

        Args:
            email (str): User's email address for registration.
            password (str): User's password for account creation.
            roles (list[str], optional): List of roles to assign to the user.
                                        Defaults to ["user"] if not provided.

        Returns:
            RegisterResponse: gRPC response containing registration confirmation and user data.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during registration.

        Note:
            - Logs registration attempts and successful registrations for monitoring
            - Default role "user" is assigned if no roles are specified
        """
        try:
            logger.info(f"Registration attempt for: {email}")
            request = RegisterRequest(
                email=email, password=password, roles=roles or ["user"]
            )
            response = self.stub.Register(request)
            logger.info(f"Registration successful for: {email}")
            return response
        except grpc.RpcError as e:
            logger.error(f"gRPC error in register: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in register: {e}")
            raise

    def logout(self, refresh_token: str):
        """
        Logout user by invalidating refresh token.

        Args:
            refresh_token (str): The refresh token to invalidate during logout.

        Returns:
            LogoutResponse: gRPC response confirming logout operation.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during logout.

        Note:
            - Logs logout requests and completion for monitoring
            - The refresh token is invalidated on the authentication service
        """
        try:
            logger.info("Logout request")
            request = LogoutRequest(refresh_token=refresh_token)
            response = self.stub.Logout(request)
            logger.info("Logout completed")
            return response
        except grpc.RpcError as e:
            logger.error(f"gRPC error in logout: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in logout: {e}")
            raise

    def refresh_token(self, refresh_token: str):
        """
        Refresh authentication tokens using a valid refresh token.

        Args:
            refresh_token (str): Valid refresh token to exchange for new tokens.

        Returns:
            RefreshTokenResponse: gRPC response containing new access and refresh tokens.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during token refresh.

        Note:
            - Logs token refresh requests and successful operations for monitoring
            - Typically used to obtain new access tokens when the current one expires
        """
        try:
            logger.info("Refresh token request")
            request = RefreshTokenRequest(refresh_token=refresh_token)
            response = self.stub.RefreshToken(request)
            logger.info("Token refresh successful")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in refresh_token: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in refresh_token: {e}")
            raise

    def verify_token(self, token: str):
        """
        Verify the validity of an authentication token.

        Args:
            token (str): The authentication token to verify.

        Returns:
            VerifyTokenResponse: gRPC response containing verification result and user claims.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during token verification.

        Note:
            - Logs token verification requests and results for monitoring
            - The response includes whether the token is valid and associated user data
        """
        try:
            logger.info("Token verification request")
            request = VerifyTokenRequest(token=token)
            response = self.stub.VerifyToken(request)
            logger.info(f"Token verification result: {response.valid}")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in verify_token: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in verify_token: {e}")
            raise

    def forgot_password(self, email: str):
        """
        Initiate password reset process for a user.

        Args:
            email (str): User's email address to send password reset instructions.

        Returns:
            ForgotPasswordResponse: gRPC response confirming the password reset request.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during password reset request.

        Note:
            - Logs password reset requests and completion for monitoring
            - Typically triggers sending a password reset email to the user
        """
        try:
            logger.info(f"Forgot password request for: {email}")
            request = ForgotPasswordRequest(email=email)
            response = self.stub.ForgotPassword(request)
            logger.info("Forgot password request completed")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in forgot_password: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in forgot_password: {e}")
            raise

    def reset_password(self, reset_token: str, new_password: str, email: str):
        """
        Reset user password using a valid reset token.

        Args:
            reset_token (str): Valid password reset token received by the user.
            new_password (str): New password to set for the user account.
            email (str): User's email address for verification.

        Returns:
            ResetPasswordResponse: gRPC response confirming password reset operation.

        Raises:
            grpc.RpcError: If gRPC call fails with status code and details.
            Exception: If any other unexpected error occurs during password reset.

        Note:
            - Logs password reset attempts and completion for monitoring
            - Requires both reset token and email for security verification
        """
        try:
            logger.info(f"Password reset for: {email}")
            request = ResetPasswordRequest(
                reset_token=reset_token, new_password=new_password, email=email
            )
            response = self.stub.ResetPassword(request)
            logger.info("Password reset completed")
            return response
        except grpc.RpcError as e:
            logger.error(
                f"gRPC error in reset_password: {e.code()} - {e.details()}"
            )
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in reset_password: {e}")
            raise
