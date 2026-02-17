import random

import pytest
from sqlmodel import Session, SQLModel, create_engine


class DBSession:
    """Context manager for creating and managing a simple SQLite DB session to use in tests."""

    def __init__(self):
        """Initialize DBSession, creating an in-memory SQLite DB and creating all the tables."""
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        SQLModel.metadata.create_all(self.engine)

    def __enter__(self) -> Session:
        """Enter the context manager, returning the new DB session."""
        self.session = Session(self.engine)
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager, closing the DB session."""
        self.session.close()

    def clean_db(self):
        """Clean the database by deleting all rows from all tables."""
        with Session(self.engine) as session:
            for table in reversed(SQLModel.metadata.sorted_tables):
                session.exec(table.delete())
            session.commit()


@pytest.fixture(scope="session")
def _db_session():
    """Fixture to initialize the DB before test session.

    Closes the DB session after the test session ends.
    """
    with DBSession() as session:
        yield session


@pytest.fixture()
def db_session(_db_session):
    """Fixture to clean the DB before each test, deleting all rows from all tables."""
    for table in reversed(SQLModel.metadata.sorted_tables):
        _db_session.exec(table.delete())
    _db_session.commit()

    yield _db_session


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    return ["pt_BR", "en_US"]


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    return random.randint(1, 99999)
