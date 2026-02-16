"""Contains user-related models."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy.sql import false
from sqlmodel import Field, Relationship, SQLModel

from .. import constants as c
from .mixins import TimestampsMixin

if TYPE_CHECKING:
    from .bucket import Bucket


class UserBase(SQLModel):
    """Base model for User."""

    email: EmailStr = Field(unique=True, index=True, max_length=512)
    full_name: str = Field(nullable=False, default=None, max_length=1024)


class UserSignup(UserBase):
    """Properties to receive via API on successful signup."""

    password: str = Field(min_length=8, max_length=128)


class UserCreate(UserBase):
    """Properties to receive via API on user creation, when done by a superuser."""

    password: str = Field(min_length=8, max_length=128)
    is_superuser: bool = False


class UserUpdate(SQLModel):
    """Properties to receive via API on User update, all optional."""

    email: EmailStr | None = Field(default=None, max_length=512)
    full_name: str | None = Field(default=None, max_length=1024)


class UpdatePassword(SQLModel):
    """Properties to receive via API on password update."""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    """Properties to return via API. ID always included."""

    id: UUID
    is_superuser: bool
    created_at: datetime
    updated_at: datetime | None


class UsersPublic(SQLModel):
    """Properties to return via API, for multiple users."""

    data: list[UserPublic]
    count: int


class User(TimestampsMixin, UserBase, table=True):
    """Database model for Users table.

    Tables and fields are created, deleted or modified with Alembic migrations
    generated based on this class.
    """

    __tablename__ = c.USER_TABLE_NAME  # type: ignore
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    is_superuser: bool = Field(
        nullable=False,
        default=False,
        sa_column_kwargs={"server_default": false()},
    )
    hashed_password: str

    buckets: list["Bucket"] = Relationship(back_populates="user")
