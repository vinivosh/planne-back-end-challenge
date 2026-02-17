"""Contains bucket-related models."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from .. import constants as c
from .mixins import TimestampsMixin

if TYPE_CHECKING:
    from .fruit import Fruit
    from .user import User


class BucketBase(SQLModel):
    """Base model for Bucket."""

    capacity: int = Field(
        nullable=False, ge=c.MIN_BUCKET_CAPACITY, le=c.MAX_BUCKET_CAPACITY
    )

    user_id: UUID = Field(
        nullable=False, foreign_key=f"{c.USER_TABLE_NAME}.id"
    )


class BucketCreate(BucketBase):
    """Properties to receive on Bucket creation."""

    fruits: list[UUID] = []


class BucketUpdate(SQLModel):
    """Properties to receive on Bucket update. All fields optional."""

    capacity: int | None = Field(
        default=None, ge=c.MIN_BUCKET_CAPACITY, le=c.MAX_BUCKET_CAPACITY
    )
    user_id: UUID | None = None
    fruits: list[UUID] = []


class BucketPublic(BucketBase):
    """Properties to return. ID always included."""

    id: UUID
    created_at: datetime
    updated_at: datetime | None


class BucketsPublic(SQLModel):
    """Properties to return, for multiple buckets."""

    data: list[BucketPublic]
    count: int


class Bucket(TimestampsMixin, BucketBase, table=True):
    """Database model for Buckets table.

    Tables and fields are created, deleted or modified with Alembic migrations
    generated based on this class.
    """

    __tablename__ = c.BUCKET_TABLE_NAME  # type: ignore
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    user: "User" = Relationship(back_populates="buckets")

    fruits: list["Fruit"] = Relationship(back_populates="bucket")
