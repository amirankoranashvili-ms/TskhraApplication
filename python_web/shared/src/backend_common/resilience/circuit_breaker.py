"""Circuit breaker pattern for protecting external service calls.

Tracks consecutive failures and transitions between closed, open, and
half-open states to fail fast when a downstream service is unhealthy.
"""

import asyncio
import logging
import time
from collections.abc import Callable, Coroutine
from enum import Enum
from typing import Any

from backend_common.exceptions import ExternalServiceException

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Possible states of a circuit breaker.

    Attributes:
        CLOSED: Normal operation; requests pass through.
        OPEN: Failing fast; requests are rejected immediately.
        HALF_OPEN: Testing recovery; a single request is allowed through.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenException(ExternalServiceException):
    """Raised when a call is rejected because the circuit breaker is open."""

    error_code = "CIRCUIT_OPEN"
    message = "Service is temporarily unavailable. Please try again later."


class CircuitBreaker:
    """Async circuit breaker that opens after consecutive failures.

    Attributes:
        name: Identifier for this circuit breaker (used in logs).
        failure_threshold: Number of failures before the circuit opens.
        recovery_timeout: Seconds to wait before transitioning to half-open.
        expected_exceptions: Exception types that count as failures.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exceptions: tuple[type[Exception], ...] = (Exception,),
    ) -> None:
        """Initialize the circuit breaker.

        Args:
            name: A descriptive name for logging and identification.
            failure_threshold: Failures required to open the circuit.
            recovery_timeout: Seconds before attempting recovery.
            expected_exceptions: Exception types treated as failures.
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Return the current circuit state, accounting for recovery timeout.

        Returns:
            The effective circuit state (may transition from OPEN to HALF_OPEN
            if the recovery timeout has elapsed).
        """
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                return CircuitState.HALF_OPEN
        return self._state

    async def call(self, func: Callable[..., Coroutine], *args, **kwargs) -> Any:
        """Execute a function through the circuit breaker.

        Args:
            func: The async callable to execute.
            *args: Positional arguments for the callable.
            **kwargs: Keyword arguments for the callable.

        Returns:
            The result of the callable.

        Raises:
            CircuitOpenException: When the circuit is open and rejecting calls.
        """
        async with self._lock:
            current_state = self.state

            if current_state == CircuitState.OPEN:
                logger.warning(
                    "Circuit '%s' is OPEN — failing fast (failures=%d)",
                    self.name, self._failure_count,
                )
                raise CircuitOpenException(
                    f"Circuit breaker '{self.name}' is open. "
                    f"Service has failed {self._failure_count} times."
                )

        try:
            result = await func(*args, **kwargs)
        except self.expected_exceptions as e:
            await self._on_failure(e)
            raise
        else:
            await self._on_success()
            return result

    async def _on_success(self) -> None:
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                logger.info("Circuit '%s' recovered — closing", self.name)
            self._state = CircuitState.CLOSED
            self._failure_count = 0

    async def _on_failure(self, error: Exception) -> None:
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.error(
                    "Circuit '%s' OPENED after %d failures: %s",
                    self.name, self._failure_count, error,
                )
            else:
                logger.warning(
                    "Circuit '%s' failure %d/%d: %s",
                    self.name, self._failure_count, self.failure_threshold, error,
                )

    async def reset(self) -> None:
        """Manually reset the circuit breaker to the closed state."""
        async with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            logger.info("Circuit '%s' manually reset", self.name)