"""Authentication module.

Handles auth-related functionalities such as creating JWT tokens, setting
cookies, checking passwords.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from . import constants as c

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(
    subject: str | Any, expires_delta: timedelta, secret_key: str | None = None
) -> str:
    """Creates a JWT access token with an expiration time."""
    if secret_key is None:
        secret_key = c.SECRET_KEY
    if secret_key is None:
        raise ValueError(
            "`secret_key` argument was not provided and environment variable "
            "`SECRET_KEY` is not set!"
        )

    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def set_token_cookie(response: Any, token: str):
    """Sets the JWT token in the response cookies.

    Args:
        response: A response object that has a set_cookie method (e.g., FastAPI
          Response).

        token: The JWT token to set in the cookie.
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
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)
