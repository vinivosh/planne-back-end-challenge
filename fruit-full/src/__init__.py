"""Start FruitFULL back-end, implemented with FastAPI.

This file is the main entry point for the application
"""

# ruff: noqa: E402
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

# Insert root directory into python module search path
_FILE_DIR = Path(__file__).parent.resolve()
_APP_DIR = _FILE_DIR.parent.resolve()
sys.path.append(str(_FILE_DIR))

import constants as c
from api import api_router

app = FastAPI(
    title=c.PROJECT_NAME,
)

app.include_router(api_router, prefix=c.API_V1_STR)


if __name__ == "__main__":
    uvicorn.run(
        "__init__:app",
        host=c.FASTAPI_HOST,
        port=c.FASTAPI_PORT,
        loop="uvloop",
        workers=c.WORKERS,
        reload=True if c.ENVIRONMENT == "dev" else False,
        log_level=c.LOG_LEVEL.lower(),
        app_dir=str(_APP_DIR),
    )
