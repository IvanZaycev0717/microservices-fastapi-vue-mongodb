import bcrypt

from logger import get_logger
from settings import settings

logger = get_logger(f"{settings.GRPC_AUTH_NAME} - password-processor")


def get_password_hash(password: str) -> str | None:
    """Generate bcrypt hash for password.

    Args:
        password: Plain text password to hash.

    Returns:
        Hashed password string if successful, None otherwise.

    Raises:
        ValueError: If password is empty.
    """
    if not password:
        error_message = "Password cannot be empty"
        logger.exception(error_message)
        raise ValueError(error_message)

    if not (
        settings.MIN_PASSWORD_LENGTH
        <= len(password)
        <= settings.MAX_PASSWORD_LENGTH
    ):
        logger.error(f"Wrong password length - {len(password)}")
        return None

    try:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        hashed_str = hashed_bytes.decode("utf-8")

        if not hashed_str.startswith("$2b$12$"):
            logger.exception("Generated hash has unexpected format")
            return None

        logger.info("Password hashed successfully")
        return hashed_str

    except Exception as e:
        logger.exception(f"Password hashing failed: {e}")
        return None


def verify_password(
    plain_password: str, hashed_password: str | bytes | None
) -> bool:
    """Safely verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password as string
        hashed_password: Hashed password (can be string, bytes, or None)

    Returns:
        True if password matches, False otherwise
    """
    if not plain_password or not hashed_password:
        logger.error("Plain password or hashed passwords cant be empty")
        return False

    try:
        if isinstance(plain_password, str):
            plain_password_bytes = plain_password.encode("utf-8")
        else:
            plain_password_bytes = plain_password

        if isinstance(hashed_password, str):
            hashed_password_bytes = hashed_password.encode("utf-8")
        elif isinstance(hashed_password, bytes):
            hashed_password_bytes = hashed_password
        else:
            logger.warning("Hashed password can be only str or bytes")
            return False

        if not hashed_password_bytes.startswith(b"$2b$"):
            logger.error("Hashed password wasnt encoded by bcrypt")
            return False

        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)

    except (ValueError, TypeError, AttributeError, UnicodeEncodeError) as e:
        logger.exception(e)
        return False
