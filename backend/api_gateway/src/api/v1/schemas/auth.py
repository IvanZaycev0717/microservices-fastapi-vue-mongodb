from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    roles: list[str] = ["user"]


class RefreshRequest(BaseModel):
    refresh_token: str = None


class VerifyRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class LoginResponse(TokenResponse):
    user_id: str
    user: dict


class RegisterResponse(TokenResponse):
    user_id: str
    user: dict


class RefreshResponse(TokenResponse):
    pass


class VerifyResponse(BaseModel):
    valid: bool
    user_id: str
    email: str
    roles: list[str]
    error: str = ""


class ForgotPasswordResponse(BaseModel):
    success: bool
    reset_token: str
    message: str


class ResetPasswordResponse(BaseModel):
    success: bool
    message: str
    user_id: str
    email: str


class LogoutResponse(BaseModel):
    message: str = "Logged out successfully"
