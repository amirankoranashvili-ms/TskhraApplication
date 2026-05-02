"""Fallback mechanisms for graceful degradation.

Provides a decorator for falling back to an alternative function or static
value on failure, and a chain executor that tries multiple strategies in order.
"""

import functools
import logging
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)


def with_fallback(
    fallback_fn: Callable[..., Coroutine] | None = None,
    fallback_value: Any = None,
    exceptions: tuple[type[Exception], ...] = (Exception,),
):
    """Decorator that provides a fallback when the decorated function fails.

    On catching a matching exception, either calls an alternative async
    function with the same arguments or returns a static value.

    Args:
        fallback_fn: Alternative async function to call on failure.
        fallback_value: Static value to return if no fallback function is set.
        exceptions: Exception types that trigger the fallback.

    Returns:
        A decorator that adds fallback behavior to an async function.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                logger.warning(
                    "Fallback activated for %s: %s. Using %s.",
                    func.__name__, e,
                    fallback_fn.__name__ if fallback_fn else "static value",
                )
                if fallback_fn:
                    return await fallback_fn(*args, **kwargs)
                return fallback_value

        return wrapper

    return decorator


class FallbackChain:
    """Executes a series of fallback strategies until one succeeds.

    Tries each strategy in order, catching exceptions and moving to
    the next one. Raises the last exception if all strategies fail.

    Attributes:
        strategies: Ordered list of async callables to try.
    """

    def __init__(self, strategies: list[Callable[..., Coroutine]]) -> None:
        """Initialize the fallback chain.

        Args:
            strategies: Ordered list of async callables to try.

        Raises:
            ValueError: When no strategies are provided.
        """
        if not strategies:
            raise ValueError("At least one fallback strategy is required")
        self.strategies = strategies

    async def execute(self, *args, **kwargs) -> Any:
        """Execute strategies in order until one succeeds.

        Args:
            *args: Positional arguments passed to each strategy.
            **kwargs: Keyword arguments passed to each strategy.

        Returns:
            The result from the first successful strategy.

        Raises:
            Exception: The last exception if all strategies fail.
        """
        last_error: Exception | None = None

        for i, strategy in enumerate(self.strategies):
            try:
                result = await strategy(*args, **kwargs)
                if i > 0:
                    logger.info(
                        "FallbackChain: strategy #%d (%s) succeeded after %d failures",
                        i + 1, strategy.__name__, i,
                    )
                return result
            except Exception as e:
                last_error = e
                logger.warning(
                    "FallbackChain: strategy #%d (%s) failed: %s",
                    i + 1, strategy.__name__, e,
                )

        raise last_error