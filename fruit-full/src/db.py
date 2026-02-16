"""Module database initialization and connection setup."""

from planne_sdk.models import User, UserCreate
from planne_sdk.use_cases import user_use_case
from sqlmodel import Session, create_engine, select

import constants as c
from logger import log

engine = create_engine(str(c.get_postgres_uri()))


# Make sure all SQLModel models are imported (planne_sdk.models) before
# initializing DB otherwise, SQLModel might fail to initialize relationships
# properly for more details:
#
# https://github.com/tiangolo/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    """Initialize the database connection.

    Also creates a superuser if none exists with the e-mail specified in the
    environment variable `FIRST_SUPERUSER_EMAIL`.

    Args:
        session:
            Database session to use for querying and creating the superuser.
    """
    user = session.exec(
        select(User).where(User.email == c.FIRST_SUPERUSER_EMAIL)
    ).first()

    if not user:
        log.info("Creating first superuser...")
        new_user = UserCreate(
            email=c.FIRST_SUPERUSER_EMAIL,
            password=c.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name=c.FIRST_SUPERUSER_FULL_NAME,
        )
        log.debug(
            "New user data: %s",
            {**new_user.model_dump(), "password": "********"},
        )

        user_use_case.create_user(session=session, user_create=new_user)

        log.info("First superuser created with success!")
