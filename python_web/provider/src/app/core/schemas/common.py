"""Common schema re-exports for the provider service.

Re-exports shared schemas from backend_common for use in API responses.
"""

from backend_common.schemas import ErrorResponse

__all__ = ["ErrorResponse"]
