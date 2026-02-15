"""This file contains the models used in the Planne SDK."""

from sqlmodel import SQLModel  # , Field


class Message(SQLModel):
    """Generic message model for API responses."""

    message: str


class Token(SQLModel):
    """JSON payload containing access token."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """Contents of JWT token."""

    sub: int | None = None
