from datetime import datetime, timedelta, timezone

from jwt import JWT, jwk_from_dict
from jwt.utils import get_int_from_datetime
from pydantic import SecretStr

from services.logger import get_logger
from settings import settings

logger = get_logger("token-processor")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

_jwt_instance = JWT()


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
    secret_key: SecretStr | None = None,
    algorithm: str = ALGORITHM,
) -> str:
    if secret_key is None:
        secret_key = SECRET_KEY
    elif not isinstance(secret_key, SecretStr):
        secret_key = SecretStr(str(secret_key))

    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    signing_key = jwk_from_dict(
        {"kty": "oct", "k": secret_key.get_secret_value()}
    )

    payload = data.copy()
    now = datetime.now(timezone.utc)

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


def verify_access_token(
    token: str,
    secret_key: SecretStr | None = None,
    algorithm: str = ALGORITHM,
) -> dict:
    if secret_key is None:
        secret_key = SECRET_KEY
    elif not isinstance(secret_key, SecretStr):
        secret_key = SecretStr(str(secret_key))

    verifying_key = jwk_from_dict(
        {"kty": "oct", "k": secret_key.get_secret_value()}
    )

    try:
        payload = _jwt_instance.decode(
            token, verifying_key, do_time_check=True, algorithms=[algorithm]
        )
        logger.info("Access token verified successfully")
        return payload
    except Exception:
        logger.exception("Access token verification failed")
        raise


def create_token_for_user(
    user_id: str,
    email: str,
    roles: list | None = None,
    expires_minutes: int | None = None,
    additional_data: dict | None = None,
) -> str:
    if roles is None:
        roles = ["user"]

    payload = {
        "sub": user_id,
        "email": email,
        "roles": roles,
    }

    if additional_data:
        payload.update(additional_data)

    expires_delta = None
    if expires_minutes is not None:
        expires_delta = timedelta(minutes=expires_minutes)

    token = create_access_token(data=payload, expires_delta=expires_delta)
    logger.info(f"Token created for user: {user_id}")

    return token


def get_user_id_from_token(token: str) -> str | None:
    try:
        payload = _jwt_instance.decode(token, do_verify=False)
        return payload.get("sub")
    except Exception:
        logger.exception("Failed to extract user ID from token")
        return None
