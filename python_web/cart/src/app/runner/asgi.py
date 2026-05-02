"""ASGI entry point for the cart service.

Exposes the ``app`` object used by ASGI servers such as Uvicorn.
"""

from src.app.runner.setup import create_app

app = create_app()
