"""Module for authentication and session-related FastAPI dependencies."""

from collections.abc import Generator
from typing import Annotated

import jwt
import planne_sdk.auth as auth
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from planne_sdk.models import TokenPayload, User
from pydantic import ValidationError
from sqlmodel import Session

import constants as c
from db import engine

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{c.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    """Get a database session.

    Yields:
        A SQLModel Session instance for database operations.
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Get the current authenticated user from the access token.

    Args:
        session:
            Database session to use for querying the user.
        token:
            The OAuth2 access token from the request.

    Returns:
        The `User` object associated with the token.

    Raises:
        HTTPException:
            If the token is invalid or expired (status code 403).
        HTTPException:
            If the user associated with the token is not found (status code 404).
    """
    try:
        payload = jwt.decode(token, c.SECRET_KEY, algorithms=[auth.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Verify that the current user is a superuser.

    Args:
        current_user:
            The currently authenticated user.

    Returns:
        The `User` object if the user is a superuser.

    Raises:
        HTTPException:
            If the user is not a superuser (status code 403).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
