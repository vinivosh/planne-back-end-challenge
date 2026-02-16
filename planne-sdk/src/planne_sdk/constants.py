"""Contains constants used throughout Planne SDK."""

import os

import dotenv

# Loading ".env" file
dotenv.load_dotenv()

LOG_LEVEL = os.environ.get("LOG_LEVEL", "WARN").upper()
if LOG_LEVEL not in [
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
]:
    LOG_LEVEL = "WARNING"


# * ###########################################################################
# * Authentication related
# * ###########################################################################

# Only used as a default value. Functions that use it should handle the case
# where it is not set (i.e. by raising a ValueError).
SECRET_KEY = os.getenv("SECRET_KEY", None)


# * ###########################################################################
# * Fruits and bucket logic
# * ###########################################################################

MIN_BUCKET_CAPACITY = 1
MAX_BUCKET_CAPACITY = 99

MIN_FRUIT_EXPIRATION_SECONDS = 1
MAX_FRUIT_EXPIRATION_SECONDS = 14 * 24 * 60 * 60  # 14 days


# * ###########################################################################
# * DB table names
# * ###########################################################################

USER_TABLE_NAME: str = "users"
BUCKET_TABLE_NAME: str = "buckets"
FRUIT_TABLE_NAME: str = "fruits"


# * ###########################################################################
# * DB credentials
# * ###########################################################################

POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

POSTGRES_DB = os.getenv("POSTGRES_DB", "planne")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")


def get_postgres_uri():
    """Build and return the PostgreSQL URI for SQLAlchemy."""
    return f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
