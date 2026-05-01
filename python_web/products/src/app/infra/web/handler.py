"""Exception handler registration for the products service.

Re-exports the shared exception handler registration function
used to configure error responses on the FastAPI application.
"""

from backend_common.error_handlers import register_exception_handlers

__all__ = ["register_exception_handlers"]
