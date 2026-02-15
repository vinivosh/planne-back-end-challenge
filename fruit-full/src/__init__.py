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

app = FastAPI(
    title=c.PROJECT_NAME,
)


if __name__ == "__main__":
    print("\n\n\n\nHello world!\n\n\n\n")

    uvicorn.run(
        "__init__:app",
        host=c.FASTAPI_HOST,
        port=c.FASTAPI_PORT,
        loop="uvloop",
        reload=True if c.ENVIRONMENT == "dev" else False,
        log_level=c.LOG_LEVEL.lower(),
        app_dir=str(_APP_DIR),
    )
