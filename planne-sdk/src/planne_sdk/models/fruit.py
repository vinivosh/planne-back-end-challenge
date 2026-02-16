"""Contains fruit-related models."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

from .. import constants as c
from .mixins import TimestampsMixin

if TYPE_CHECKING:
    from . import Bucket, User


class FruitBase(SQLModel):
    """Base model for Fruit."""

    name: str = Field(
        nullable=False,
        min_length=c.MIN_FRUIT_NAME_LENGTH,
        max_length=c.MAX_FRUIT_NAME_LENGTH,
    )
    price: int = Field(
        description="Price of the fruit in cents",
        nullable=False,
        ge=c.MIN_FRUIT_PRICE_CENTS,
        le=c.MAX_FRUIT_PRICE_CENTS,
    )

    bucket_id: UUID | None = Field(
        default=None, nullable=True, foreign_key=f"{c.BUCKET_TABLE_NAME}.id"
    )

    user_id: UUID = Field(
        nullable=False, foreign_key=f"{c.USER_TABLE_NAME}.id"
    )


class FruitCreate(FruitBase):
    """Properties to receive via API on Fruit creation."""

    expiration_seconds: int = Field(
        description="Expiration time of the fruit in seconds, relative to the time of creation (UTC)",
        nullable=False,
        ge=c.MIN_FRUIT_EXPIRATION_SECONDS,
        le=c.MAX_FRUIT_EXPIRATION_SECONDS,
    )


class FruitUpdate(SQLModel):
    """Properties to receive via API on Fruit update. All fields optional."""

    name: str | None = Field(
        min_length=c.MIN_FRUIT_NAME_LENGTH,
        max_length=c.MAX_FRUIT_NAME_LENGTH,
    )
    price: int | None = Field(
        description="Price of the fruit in cents",
        ge=c.MIN_FRUIT_PRICE_CENTS,
        le=c.MAX_FRUIT_PRICE_CENTS,
    )
    expiration_seconds: int | None = Field(
        description="Expiration time of the fruit in seconds, relative to the time of creation (UTC)",
        ge=c.MIN_FRUIT_EXPIRATION_SECONDS,
        le=c.MAX_FRUIT_EXPIRATION_SECONDS,
    )

    bucket_id: UUID | None = None


class FruitPublic(FruitBase):
    """Properties to return via API."""

    id: UUID
    expires_at: datetime
    created_at: datetime
    updated_at: datetime | None


class FruitsPublic(SQLModel):
    """Properties to return via API, for multiple fruits."""

    data: list[FruitPublic]
    count: int


class Fruit(TimestampsMixin, FruitBase, table=True):
    """Database model for Fruits table.

    Tables and fields are created, deleted or modified with Alembic migrations
    generated based on this class.
    """

    __tablename__ = c.FRUIT_TABLE_NAME  # type: ignore
    __table_args__ = (
        # Enforces that `expires_at` is always at least
        # `c.MIN_FRUIT_EXPIRATION_SECONDS` seconds after`created_at`.
        sa.CheckConstraint(
            "expires_at > created_at",
            name="check_expires_at_after_created_at",
        ),
        {"extend_existing": True},
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    expires_at: datetime = Field(
        nullable=False,
        sa_type=sa.DateTime(timezone=False),  # pyright: ignore[reportArgumentType]
    )

    bucket: Optional["Bucket"] | None = Relationship(back_populates="fruits")

    user: Optional["User"] = Relationship(back_populates="fruits")
