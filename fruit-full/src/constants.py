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


# * ###########################################################################
# * Other server configurations
# * ###########################################################################

API_V1_STR = "/api/v1"
