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
    def __init__(self):
        self.channel = grpc.insecure_channel(
            f"{settings.API_GATEWAY_AUTH_HOST}:{settings.GRPC_AUTH_PORT}"
        )
        self.stub = AuthServiceStub(self.channel)
        logger.info("AuthClient initialized")

    def login(self, email: str, password: str):
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
