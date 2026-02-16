"""This file contains the models used in the Planne SDK."""

from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

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


class TimestampsMixin:
    """Simple mixin for `created_at` and `updated_at` UTC datetime fields.

    Both fields are automatically set to the current UTC time when a new record
    is created. The `updated_at` field is automatically updated to the current
    UTC time whenever the record is updated.

    Example:
        ```
        class MyModel(TimestampsMixin, SQLModel):
            pass
        ```
    """

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=sa.DateTime(timezone=False),  # pyright: ignore[reportArgumentType]
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )

    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=sa.DateTime(timezone=False),  # pyright: ignore[reportArgumentType]
        sa_column_kwargs={
            "onupdate": sa.func.now(),
            "server_default": sa.func.now(),
        },
        nullable=True,
    )