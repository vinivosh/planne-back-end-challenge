"""Contains bucket-related models."""

from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from .. import constants as c
from . import TimestampsMixin


class BucketBase(SQLModel):
    """Base model for Bucket."""

    capacity: int = Field(
        nullable=False, ge=c.MIN_BUCKET_CAPACITY, le=c.MAX_BUCKET_CAPACITY
    )


class BucketPublic(BucketBase):
    """Properties to return via API. ID always included."""

    id: UUID


class BucketsPublic(SQLModel):
    """Properties to return via API, for multiple buckets."""

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
