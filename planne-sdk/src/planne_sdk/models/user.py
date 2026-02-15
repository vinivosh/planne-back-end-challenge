"""Contains user-related models."""

from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy.sql import false
from sqlmodel import Field, SQLModel

from .. import constants as c


class UserBase(SQLModel):
    """Base model for User."""

    email: EmailStr = Field(unique=True, index=True, max_length=512)
    full_name: str = Field(nullable=False, default=None, max_length=1024)


class User(UserBase, table=True):
    """Database model for User table.

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
