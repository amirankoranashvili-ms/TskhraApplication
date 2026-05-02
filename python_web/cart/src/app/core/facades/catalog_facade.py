"""Facade for communicating with the external catalog/products service.

Wraps HTTP calls to the catalog service with resilience patterns including
circuit breaker, retry, bulkhead, and in-memory caching as a fallback.
"""

import logging

import httpx

from backend_common.resilience.circuit_breaker import CircuitBreaker
from backend_common.resilience.retry import Retry
from backend_common.resilience.bulkhead import Bulkhead

from src.app.core.config import settings

logger = logging.getLogger(__name__)

_circuit = CircuitBreaker(
    name="catalog-service",
    failure_threshold=settings.CATALOG_CIRCUIT_FAILURE_THRESHOLD,
    recovery_timeout=settings.CATALOG_CIRCUIT_RECOVERY_TIMEOUT,
    expected_exceptions=(httpx.RequestError, httpx.HTTPStatusError),
)
_retry = Retry(
    max_attempts=settings.CATALOG_RETRY_MAX_ATTEMPTS,
    backoff_base=settings.CATALOG_RETRY_BACKOFF_BASE,
    retryable=(httpx.ConnectError, httpx.ReadTimeout),
)
_bulkhead = Bulkhead(
    name="catalog",
    max_concurrent=settings.CATALOG_BULKHEAD_MAX_CONCURRENT,
    max_wait=settings.CATALOG_BULKHEAD_MAX_WAIT,
)


class CatalogFacade:
    """Resilient facade for fetching product data from the catalog service."""

    def __init__(self, catalog_service_url: str) -> None:
        """Initialize the catalog facade.

        Args:
            catalog_service_url: Base URL of the catalog/products service.
        """
        self.catalog_service_url = catalog_service_url
        self._product_cache: dict[int, dict] = {}

    async def _fetch_product(self, product_id: int) -> dict:
        """Fetch product data from the catalog service via HTTP.

        Args:
            product_id: The product identifier to look up.

        Returns:
            Product data dictionary, or empty dict if not found.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.catalog_service_url}/{product_id}",
                timeout=settings.CATALOG_REQUEST_TIMEOUT,
            )
            if response.status_code == 404:
                return {}
            response.raise_for_status()
            data = response.json()
            return data.get("product", data)

    async def _get_cached_product(self, product_id: int) -> dict:
        """Return a previously cached product as a fallback.

        Args:
            product_id: The product identifier to look up in cache.

        Returns:
            Cached product data dictionary, or empty dict if not cached.
        """
        cached = self._product_cache.get(product_id)
        if cached:
            logger.info("Returning cached product %s (catalog unavailable)", product_id)
            return cached
        return {}

    async def get_product(self, product_id: int) -> dict:
        """Retrieve product data with full resilience (circuit breaker, retry, bulkhead).

        Falls back to cached data if all resilience layers fail.

        Args:
            product_id: The product identifier to retrieve.

        Returns:
            Product data dictionary, or empty dict if unavailable.
        """
        try:
            async with _bulkhead:
                result = await _circuit.call(
                    _retry.execute,
                    self._fetch_product,
                    product_id,
                )

                if result:
                    self._product_cache[product_id] = result
                return result

        except Exception as e:
            logger.warning(
                "All resilience layers failed for product %s: %s. Trying fallback.",
                product_id,
                e,
            )
            return await self._get_cached_product(product_id)

    async def validate_product_available(self, product_id: int, quantity: int) -> bool:
        """Check whether a product is active and has sufficient stock.

        Args:
            product_id: The product identifier to validate.
            quantity: The requested quantity.

        Returns:
            True if the product is active and stock is sufficient.
        """
        product = await self.get_product(product_id)
        if not product:
            return False

        stock = product.get("stock_quantity", 0)
        is_active = product.get("is_active", True)

        return is_active and stock >= quantity
