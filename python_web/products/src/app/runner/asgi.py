"""ASGI application entry point.

Exposes the configured FastAPI application instance for ASGI servers
such as Uvicorn.
"""

from src.app.runner.setup import create_app

app = create_app()
