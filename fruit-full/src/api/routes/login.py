"""Docstring for fruit-full.src.api.routes.login."""

from fastapi import APIRouter, Response

import constants as c

router = APIRouter()


@router.get("/hello_world")
def hello_world(
    response: Response,
) -> Response:
    """Hello world route."""
    return Response(
        content=f"Hello from {c.PROJECT_NAME}!", media_type="text/plain"
    )
