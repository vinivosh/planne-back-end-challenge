"""Authentication module.

Handles auth-related functionalities such as creating JWT tokens, setting
cookies, and hashing passwords using Argon2id.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from . import constants as c

pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__memory_cost=65536,  # 64 MiB
    argon2__time_cost=3,
    argon2__parallelism=4,
    deprecated="auto",
)


JWT_ENCODING_ALGORITHM = "HS256"


def create_access_token(
    subject: str | Any, expires_delta: timedelta, secret_key: str | None = None
) -> str:
    """Create a JWT access token with an expiration time.

    Args:
        subject:
            The subject (typically user ID) to encode in the token.
        expires_delta:
            The time delta specifying how long the token should remain valid.
        secret_key:
            The secret key used to sign the token. If not provided, uses the
            SECRET_KEY from environment variables.

    Returns:
        The encoded JWT access token as a string.

    Raises:
        ValueError:
            If the secret_key is not provided and the SECRET_KEY environment
            variable is not set.
    """
    if secret_key is None:
        secret_key = c.SECRET_KEY
    if secret_key is None:
        raise ValueError(
            "`secret_key` argument was not provided and environment variable "
            "`SECRET_KEY` is not set!"
        )

    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, secret_key, algorithm=JWT_ENCODING_ALGORITHM
    )
    return encoded_jwt


def set_token_cookie(response: Any, token: str):
    """Set the JWT token in the response cookies.

    Args:
        response:
            A response object that has a `set_cookie()` method (e.g., FastAPI
            Response).
        token:
            The JWT token to set in the cookie.
    """
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=False,
        samesite="none",
        max_age=7200,  # In seconds
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password:
            The plain text password to verify.
        hashed_password:
            The hashed password to verify against.

    Returns:
        `True` if the password matches the hash, `False` otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using the Argon2id algorithm.

    Salting is handled automatically by `passlib`.

    Args:
        password:
            The plain text password to hash.

    Returns:
        The hashed password string, already salted.
    """
    return pwd_context.hash(password)
