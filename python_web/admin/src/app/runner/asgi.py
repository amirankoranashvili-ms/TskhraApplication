"""ASGI entry point that exposes the FastAPI application instance."""

from src.app.runner.setup import create_app

app = create_app()
