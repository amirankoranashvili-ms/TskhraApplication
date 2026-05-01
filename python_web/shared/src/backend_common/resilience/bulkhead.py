"""Bulkhead pattern for limiting concurrent access to a resource.

Implements the bulkhead resilience pattern using an async semaphore,
preventing any single service from monopolizing system resources.
"""

import asyncio
import logging

from backend_common.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)


class BulkheadFullException(ExternalServiceException):
    """Raised when the bulkhead has no available slots and the wait time is exceeded."""
    error_code = "SERVICE_OVERLOADED"
    message = "Service is overloaded. Please try again later."


class Bulkhead:
    """Limits concurrent access to a resource using a semaphore.

    Use as an async context manager to acquire a slot before accessing
    a protected resource. If the bulkhead is full and the wait time
    is exceeded, a ``BulkheadFullException`` is raised.
    """
    def __init__(
        self,
        name: str,
        max_concurrent: int = 10,
        max_wait: float = 5.0,
    ) -> None:
        """Initialize the bulkhead.

        Args:
            name: A descriptive name for this bulkhead (used in logging).
            max_concurrent: Maximum number of concurrent operations allowed.
            max_wait: Maximum seconds to wait for a slot before raising.
        """
        self.name = name
        self.max_concurrent = max_concurrent
        self.max_wait = max_wait
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active = 0

    @property
    def active_count(self) -> int:
        """Return the number of currently active operations."""
        return self._active

    @property
    def available_slots(self) -> int:
        """Return the number of available slots."""
        return self.max_concurrent - self._active

    async def __aenter__(self):
        try:
            await asyncio.wait_for(
                self._semaphore.acquire(), timeout=self.max_wait
            )
        except asyncio.TimeoutError:
            logger.error(
                "Bulkhead '%s' full: %d/%d slots used, waited %.1fs",
                self.name, self._active, self.max_concurrent, self.max_wait,
            )
            raise BulkheadFullException(
                f"Service '{self.name}' has reached max concurrent requests "
                f"({self.max_concurrent}). Try again later."
            )
        self._active += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._active -= 1
        self._semaphore.release()
        return False