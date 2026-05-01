"""Timeout utilities for async operations.

Provides both a direct execution helper and a decorator to enforce time
limits on coroutines, raising a ``ServiceTimeoutException`` on expiry.
"""

import asyncio
import functools
import logging
from collections.abc import Coroutine
from typing import Any

from backend_common.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)


class ServiceTimeoutException(ExternalServiceException):
    """Raised when an async operation exceeds its allowed time limit."""
    error_code = "SERVICE_TIMEOUT"
    message = "Service did not respond in time."


async def execute_with_timeout(coro: Coroutine, seconds: float) -> Any:
    """Execute a coroutine with a timeout.

    Args:
        coro: The coroutine to execute.
        seconds: Maximum number of seconds to wait.

    Returns:
        The result of the coroutine.

    Raises:
        ServiceTimeoutException: If the coroutine does not complete in time.
    """
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        logger.error("Operation timed out after %.1fs", seconds)
        raise ServiceTimeoutException(
            f"Operation timed out after {seconds}s"
        )


def with_timeout(seconds: float):
    """Decorator that enforces a timeout on an async function.

    Args:
        seconds: Maximum number of seconds the decorated function may run.

    Returns:
        A decorator that wraps the function with timeout enforcement.

    Raises:
        ServiceTimeoutException: If the function does not complete in time.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs), timeout=seconds
                )
            except asyncio.TimeoutError:
                logger.error(
                    "%s timed out after %.1fs", func.__name__, seconds
                )
                raise ServiceTimeoutException(
                    f"{func.__name__} timed out after {seconds}s"
                )

        return wrapper

    return decorator