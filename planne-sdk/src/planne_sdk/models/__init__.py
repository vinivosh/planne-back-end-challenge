"""This file contains the models used in the Planne SDK."""

from uuid import UUID

from sqlmodel import SQLModel

from .bucket import *
from .fruit import *
from .user import *


class Message(SQLModel):
    """Generic message model for API responses."""

    message: str


class Token(SQLModel):
    """JSON payload containing access token."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """Contents of JWT token."""

    sub: UUID | None = None
