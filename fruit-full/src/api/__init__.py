"""Module containing all the API routes for the application."""

from fastapi import APIRouter

from api.routes import login

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login", tags=["login"])
