"""ASGI entry point for the payment service.

Exposes the ``app`` object that ASGI servers (e.g. Uvicorn) import directly.
"""

from src.app.runner.setup import create_app

app = create_app()
