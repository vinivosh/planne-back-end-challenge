"""Implementation of user-related use cases (CRUD)."""

from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from ..auth import get_password_hash, verify_password
from ..models import User, UserCreate, UserSignup, UserUpdate


def create_user(
    *, session: Session, user_create: UserCreate | UserSignup
) -> User:
    """Create a new user.

    Args:
        session:
            Database session to use for adding and committing the new user.
        user_create:
            UserCreate or UserSignup object, containing user information.

    Returns:
        The newly created `User` object.
    """
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(
    *, session: Session, db_user: User, user_in: UserUpdate
) -> Any:
    """Update an existing user.

    Args:
        session:
            Database session to use for updating and committing the user.
        db_user:
            The existing user object to update.
        user_in:
            UserUpdate object, containing the fields and values to update.

    Returns:
        The updated `User` object.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user(*, session: Session, id: UUID | str) -> User | None:
    """Get a user by ID.

    Args:
        session:
            Database session to use for the query.
        id:
            ID of the user to retrieve.

    Returns:
        The `User` object if found, or `None` if no user with the given
        ID exists.
    """
    return session.get(User, id)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Get a user by email.

    Args:
        session:
            Database session to use for the query.
        email:
            Email address of the user to retrieve.

    Returns:
        The `User` object if found, or `None` if no user with the given
        email exists.
    """
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(
    *, session: Session, email: str, password: str
) -> User | None:
    """Authenticate a user by email and password.

    Args:
        session:
            Database session to use for the query.
        email:
            Email of the user to authenticate.
        password:
            Plain text password to verify against the stored hashed password.

    Returns:
        The authenticated `User` object if authentication is successful, or
        `None` if authentication fails (user not found or incorrect password).
    """
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def update_user_password(session: Session, user: User, new_password: str):
    """Update the password of a user.

    Args:
        session:
            Database session to use for updating and committing the password.
        user:
            The user object whose password will be updated.
        new_password:
            The new plain text password to set for the user.
    """
    user.hashed_password = get_password_hash(new_password)
    session.commit()
    session.refresh(user)
