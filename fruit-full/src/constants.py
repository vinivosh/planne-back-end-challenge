"""Module containing all the constants used in the application. Most of these are loaded from environment variables."""

import os
from multiprocessing import cpu_count

import dotenv

_LOG_LEVELS = [
    "CRITICAL",
    "FATAL",
    "ERROR",
    "WARN",
    "WARNING",
    "INFO",
    "DEBUG",
]
_DEFAULT_WORKERS_PER_THREAD = 4

# * ###########################################################################
# * Environment variables
# * ###########################################################################

# Loading ".env" file
dotenv.load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "prd").lower()
if ENVIRONMENT not in ["dev", "prd", "stg"]:
    raise ValueError(
        "Environment variable ENVIRONMENT must be one of: dev, prd, stg"
    )

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
if LOG_LEVEL not in _LOG_LEVELS:
    raise ValueError(
        f"Environment variable LOG_LEVEL must be one of: {', '.join(_LOG_LEVELS)}"
    )

try:
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))
except ValueError:
    raise ValueError(
        "Environment variable FASTAPI_PORT must be a valid integer"
    )

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
PROJECT_NAME = os.getenv("PROJECT_NAME", "FruitFULL")

WORKERS = os.environ.get("WORKERS", None)
if WORKERS is None:
    WORKERS = cpu_count() * _DEFAULT_WORKERS_PER_THREAD
else:
    try:
        WORKERS = int(WORKERS)
    except ValueError:
        raise ValueError(
            "Environment variable WORKERS must be a valid integer"
        )

# Secret key used for JWT token encoding and decoding
SECRET_KEY = os.getenv("SECRET_KEY", None)
if SECRET_KEY is None:
    raise ValueError("Environment variable SECRET_KEY is not set!")


# * ###########################################################################
# * DB credentials
# * ###########################################################################

POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

POSTGRES_DB = os.getenv("POSTGRES_DB", "planne")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")


def get_postgres_uri():
    """Build and return the PostgreSQL URI for SQLAlchemy.

    Built using the `POSTGRES_*` environment variables.

    Returns:
        str: A PostgreSQL URI string in the format `postgresql+psycopg://<POSTGRES_USER>:<POSTGRES_PASSWORD>@<POSTGRES_SERVER>:<POSTGRES_PORT>/<POSTGRES_DB>`
    """
    return f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


# * ###########################################################################
# * First super user credentials
# * ###########################################################################

FIRST_SUPERUSER_EMAIL = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@mail.com")
FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD", "12345678")
FIRST_SUPERUSER_FULL_NAME = os.getenv(
    "FIRST_SUPERUSER_FULL_NAME", "Vinícius Administrador"
)


# * ###########################################################################
# * Other server configurations
# * ###########################################################################

API_V1_STR = "/api/v1"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours

CLEANUP_EXPIRED_FRUITS_CRON_SCHEDULE = (
    "0 7 * * 1"  # Weekly -> 3 AM GMT-3/BRL (6 AM UTC) every monday
)
