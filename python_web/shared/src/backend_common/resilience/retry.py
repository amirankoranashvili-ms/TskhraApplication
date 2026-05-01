"""Retry logic with exponential backoff and optional jitter.

Provides both a class-based ``Retry`` executor and a ``retry`` decorator
for transparently retrying failed async operations.
"""

import asyncio
import functools
import logging
import random
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)


class MaxRetriesExceeded(Exception):
    """Raised when all retry attempts have been exhausted.

    Attributes:
        attempts: Total number of attempts made.
        last_error: The exception from the final attempt.
    """

    def __init__(self, attempts: int, last_error: Exception) -> None:
        """Initialize with attempt count and last error.

        Args:
            attempts: Total number of attempts made.
            last_error: The exception from the final attempt.
        """
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(
            f"Failed after {attempts} attempts. Last error: {last_error}"
        )


class Retry:
    """Configurable retry executor with exponential backoff.

    Attributes:
        max_attempts: Maximum number of execution attempts.
        backoff_base: Base delay in seconds for exponential backoff.
        max_delay: Maximum delay cap in seconds.
        retryable: Exception types that trigger a retry.
        jitter: Whether to add randomized jitter to delays.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        backoff_base: float = 1.0,
        max_delay: float = 30.0,
        retryable: tuple[type[Exception], ...] = (Exception,),
        jitter: bool = True,
    ) -> None:
        """Initialize the retry configuration.

        Args:
            max_attempts: Maximum number of attempts before giving up.
            backoff_base: Base delay multiplier in seconds.
            max_delay: Upper bound for the computed delay.
            retryable: Tuple of exception types eligible for retry.
            jitter: Add random jitter to prevent thundering herd.
        """
        self.max_attempts = max_attempts
        self.backoff_base = backoff_base
        self.max_delay = max_delay
        self.retryable = retryable
        self.jitter = jitter

    def _calculate_delay(self, attempt: int) -> float:
        delay = min(self.backoff_base * (2 ** attempt), self.max_delay)
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        return delay

    async def execute(self, func: Callable[..., Coroutine], *args, **kwargs) -> Any:
        """Execute a function with automatic retries on failure.

        Args:
            func: The async callable to execute.
            *args: Positional arguments for the callable.
            **kwargs: Keyword arguments for the callable.

        Returns:
            The result of the callable on a successful attempt.

        Raises:
            MaxRetriesExceeded: When all attempts have been exhausted.
        """
        last_error: Exception | None = None

        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except self.retryable as e:
                last_error = e
                if attempt < self.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        "Retry %d/%d for %s after %.1fs: %s",
                        attempt + 1, self.max_attempts, func.__name__, delay, e,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "All %d retries exhausted for %s: %s",
                        self.max_attempts, func.__name__, e,
                    )

        raise MaxRetriesExceeded(self.max_attempts, last_error)


def retry(
    max_attempts: int = 3,
    backoff_base: float = 1.0,
    max_delay: float = 30.0,
    retryable: tuple[type[Exception], ...] = (Exception,),
):
    """Decorator that adds retry logic with exponential backoff to an async function.

    Args:
        max_attempts: Maximum number of attempts before giving up.
        backoff_base: Base delay multiplier in seconds.
        max_delay: Upper bound for the computed delay.
        retryable: Tuple of exception types eligible for retry.

    Returns:
        A decorator that wraps an async function with retry behavior.
    """
    def decorator(func):
        retryer = Retry(
            max_attempts=max_attempts,
            backoff_base=backoff_base,
            max_delay=max_delay,
            retryable=retryable,
        )

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await retryer.execute(func, *args, **kwargs)

        return wrapper

    return decorator