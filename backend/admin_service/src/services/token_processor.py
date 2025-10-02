from datetime import datetime, timedelta
from typing import Any

from jwt import JWT, jwk_from_dict
from jwt.exceptions import JWTException
from jwt.utils import get_int_from_datetime
from pydantic import SecretStr

from services.logger import get_logger
from settings import settings

logger = get_logger("token-processor")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

_jwt_instance = JWT()


def create_jwt_token(
    data: dict[str, Any],
    expires_delta: timedelta,
    secret_key: SecretStr | None = SECRET_KEY,
    algorithm: str = ALGORITHM,
) -> str:
    """Create JWT token with specified payload and expiration.

    Args:
        data (dict[str, Any]): Payload data to include in token.
        expires_delta (timedelta): Token expiration time delta.
        secret_key (SecretStr | None): Secret key for signing.
        algorithm (str): Algorithm to use for signing.

    Returns:
        str: Encoded JWT token string.
    """
    signing_key = jwk_from_dict(
        {"kty": "oct", "k": secret_key.get_secret_value()}
    )

    payload = data.copy()
    now = datetime.now()

    payload.update(
        {
            "iat": get_int_from_datetime(now),
            "exp": get_int_from_datetime(now + expires_delta),
            "nbf": get_int_from_datetime(now),
        }
    )

    compact_jws = _jwt_instance.encode(payload, signing_key, alg=algorithm)
    logger.info("Access token created successfully")

    return compact_jws


def verify_jwt_token(
    token: str,
    secret_key: SecretStr | None = SECRET_KEY,
    algorithm: str = ALGORITHM,
) -> dict:
    """Verify and decode JWT token.

    Args:
        token (str): JWT token string to verify.
        secret_key (SecretStr | None): Secret key for verification.
        algorithm (str): Algorithm to use for verification.

    Returns:
        dict: Decoded token payload.

    Raises:
        JWTException: If token verification fails.
    """
    verifying_key = jwk_from_dict(
        {"kty": "oct", "k": secret_key.get_secret_value()}
    )

    try:
        payload = _jwt_instance.decode(
            token, verifying_key, do_time_check=True, algorithms=[algorithm]
        )
        logger.info("Token verified successfully")
        return payload
    except JWTException:
        logger.exception("Token verification failed")
        raise


def create_token_for_user(
    user_id: str,
    email: str,
    expires_delta: timedelta,
    roles: list | None = None,
) -> str:
    """Create JWT token for user authentication.

    Args:
        user_id (str): User identifier.
        email (str): User's email address.
        expires_delta (timedelta): Token expiration time delta.
        roles (list | None): List of user roles.

    Returns:
        str: Encoded JWT token string.
    """
    if roles is None:
        roles = ["user"]

    payload = {
        "sub": user_id,
        "email": email,
        "roles": roles,
    }
    token = create_jwt_token(data=payload, expires_delta=expires_delta)
    logger.info(f"Token created for user: {user_id}")

    return token


def get_user_id_from_token(token: str) -> str | None:
    """Extract user ID from JWT token without verification.

    Args:
        token (str): JWT token string.

    Returns:
        str | None: User ID if found, None otherwise.
    """
    try:
        payload = _jwt_instance.decode(token, do_verify=False)
        return payload.get("sub")
    except Exception:
        logger.exception("Failed to extract user ID from token")
        return None
