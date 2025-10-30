from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import (
    ClassVar as _ClassVar,
    Optional as _Optional,
    Union as _Union,
)

from google.protobuf import descriptor as _descriptor, message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class LoginRequest(_message.Message):
    __slots__ = ("email", "password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    def __init__(
        self, email: _Optional[str] = ..., password: _Optional[str] = ...
    ) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = (
        "access_token",
        "refresh_token",
        "token_type",
        "user_id",
        "expires_in",
        "user",
    )
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    token_type: str
    user_id: str
    expires_in: int
    user: User
    def __init__(
        self,
        access_token: _Optional[str] = ...,
        refresh_token: _Optional[str] = ...,
        token_type: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        expires_in: _Optional[int] = ...,
        user: _Optional[_Union[User, _Mapping]] = ...,
    ) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("email", "password", "roles")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        email: _Optional[str] = ...,
        password: _Optional[str] = ...,
        roles: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class RegisterResponse(_message.Message):
    __slots__ = (
        "access_token",
        "refresh_token",
        "token_type",
        "user_id",
        "expires_in",
        "user",
    )
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    token_type: str
    user_id: str
    expires_in: int
    user: User
    def __init__(
        self,
        access_token: _Optional[str] = ...,
        refresh_token: _Optional[str] = ...,
        token_type: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        expires_in: _Optional[int] = ...,
        user: _Optional[_Union[User, _Mapping]] = ...,
    ) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ("refresh_token",)
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    def __init__(self, refresh_token: _Optional[str] = ...) -> None: ...

class LogoutResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(
        self, success: bool = ..., message: _Optional[str] = ...
    ) -> None: ...

class RefreshTokenRequest(_message.Message):
    __slots__ = ("refresh_token",)
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    def __init__(self, refresh_token: _Optional[str] = ...) -> None: ...

class RefreshTokenResponse(_message.Message):
    __slots__ = ("access_token", "refresh_token", "token_type", "expires_in")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    def __init__(
        self,
        access_token: _Optional[str] = ...,
        refresh_token: _Optional[str] = ...,
        token_type: _Optional[str] = ...,
        expires_in: _Optional[int] = ...,
    ) -> None: ...

class VerifyTokenRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class VerifyTokenResponse(_message.Message):
    __slots__ = ("valid", "user_id", "email", "roles", "error")
    VALID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    user_id: str
    email: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    error: str
    def __init__(
        self,
        valid: bool = ...,
        user_id: _Optional[str] = ...,
        email: _Optional[str] = ...,
        roles: _Optional[_Iterable[str]] = ...,
        error: _Optional[str] = ...,
    ) -> None: ...

class ForgotPasswordRequest(_message.Message):
    __slots__ = ("email",)
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

class ForgotPasswordResponse(_message.Message):
    __slots__ = ("success", "reset_token", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    RESET_TOKEN_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    reset_token: str
    message: str
    def __init__(
        self,
        success: bool = ...,
        reset_token: _Optional[str] = ...,
        message: _Optional[str] = ...,
    ) -> None: ...

class ResetPasswordRequest(_message.Message):
    __slots__ = ("reset_token", "new_password", "email")
    RESET_TOKEN_FIELD_NUMBER: _ClassVar[int]
    NEW_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    reset_token: str
    new_password: str
    email: str
    def __init__(
        self,
        reset_token: _Optional[str] = ...,
        new_password: _Optional[str] = ...,
        email: _Optional[str] = ...,
    ) -> None: ...

class ResetPasswordResponse(_message.Message):
    __slots__ = ("success", "message", "user_id", "email")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    user_id: str
    email: str
    def __init__(
        self,
        success: bool = ...,
        message: _Optional[str] = ...,
        user_id: _Optional[str] = ...,
        email: _Optional[str] = ...,
    ) -> None: ...

class User(_message.Message):
    __slots__ = (
        "id",
        "email",
        "roles",
        "is_banned",
        "created_at",
        "last_login_at",
    )
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    IS_BANNED_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_LOGIN_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    is_banned: bool
    created_at: str
    last_login_at: str
    def __init__(
        self,
        id: _Optional[str] = ...,
        email: _Optional[str] = ...,
        roles: _Optional[_Iterable[str]] = ...,
        is_banned: bool = ...,
        created_at: _Optional[str] = ...,
        last_login_at: _Optional[str] = ...,
    ) -> None: ...
