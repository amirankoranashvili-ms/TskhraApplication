"""ASGI entry point for the provider service.

Creates the FastAPI application instance used by ASGI servers.
"""

from src.app.runner.setup import create_app

app = create_app()
