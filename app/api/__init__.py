# app/api/__init__.py
from .database_routes import router as database_router

__all__ = ["database_router"]
