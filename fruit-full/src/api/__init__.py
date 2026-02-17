"""Module containing all the API routes for the application."""

from fastapi import APIRouter

from api.routes import bucket, fruit, login, user

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(fruit.router, prefix="/fruit", tags=["fruit"])
api_router.include_router(bucket.router, prefix="/bucket", tags=["bucket"])