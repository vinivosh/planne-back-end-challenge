"""Contains fruit-related models."""

from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from .. import constants as c
from . import TimestampsMixin


class FruitBase(SQLModel):
    """Base model for Fruit."""

    expiration_seconds: int = Field(
        nullable=False,
        ge=c.MIN_FRUIT_EXPIRATION_SECONDS,
        le=c.MAX_FRUIT_EXPIRATION_SECONDS,
    )


class FruitPublic(FruitBase):
    """Properties to return via API. ID always included."""

    id: UUID


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
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(default_factory=uuid4, primary_key=True)
