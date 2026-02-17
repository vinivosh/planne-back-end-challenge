"""Module with useful mixins for Planne SDK."""

from datetime import UTC, datetime

import sqlalchemy as sa
from sqlmodel import Field


class TimestampsMixin:
    """Simple mixin for `created_at` and `updated_at` UTC datetime fields.

    Both fields are automatically set to the current UTC time when a new record
    is created. The `updated_at` field is automatically updated to the current
    UTC time whenever the record is updated (with SQLAlchemy / SQLModel).

    Example:
        ```
        class MyModel(TimestampsMixin, SQLModel):
            pass
        ```

    Credits:
        Based on suggestions from https://github.com/fastapi/sqlmodel/issues/252
    """

    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=sa.DateTime(),  # pyright: ignore[reportArgumentType]
        sa_column_kwargs={"server_default": sa.func.now()},
        nullable=False,
    )

    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=sa.DateTime(),  # pyright: ignore[reportArgumentType]
        sa_column_kwargs={
            "onupdate": sa.func.now(),
            "server_default": sa.func.now(),
        },
        nullable=True,
    )
