"""HTTP client for communicating with the catalog (products) service.

Provides resilient HTTP calls to the catalog service using circuit breaker,
retry, and bulkhead patterns.
"""

import logging
from typing import Any

import httpx
from backend_common.resilience.bulkhead import Bulkhead
from backend_common.resilience.circuit_breaker import CircuitBreaker
from backend_common.resilience.retry import Retry

from src.app.core.config import settings

logger = logging.getLogger(__name__)

_circuit = CircuitBreaker(
    name="catalog-service",
    failure_threshold=5,
    recovery_timeout=30,
    expected_exceptions=(httpx.RequestError, httpx.HTTPStatusError),
)
_retry = Retry(
    max_attempts=3,
    backoff_base=0.5,
    retryable=(httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout),
)
_bulkhead = Bulkhead(name="catalog", max_concurrent=20, max_wait=5.0)


class CatalogHttpClient:
    """HTTP client for the catalog service with resilience patterns.

    Wraps httpx.AsyncClient with circuit breaker, retry, and bulkhead
    patterns for fault-tolerant communication with the catalog service.
    """

    def __init__(self, client: httpx.AsyncClient):
        """Initialize with an httpx async client.

        Args:
            client: Pre-configured httpx async client for the catalog service.
        """
        self._client = client

    async def _fetch_product(self, product_id: int) -> dict[str, Any] | None:
        """Fetch a product from the catalog service.

        Args:
            product_id: ID of the product to fetch.

        Returns:
            Product data dict, or None if not found.
        """
        response = await self._client.get(f"/{product_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def _fetch_vendor_products(
        self, supplier_id: int, page: int, limit: int
    ) -> dict[str, Any] | None:
        """Fetch paginated vendor products from the catalog service.

        Args:
            supplier_id: ID of the vendor.
            page: Page number.
            limit: Items per page.

        Returns:
            Paginated product data dict.
        """
        response = await self._client.get(
            "/", params={"supplier_id": supplier_id, "page": page, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    async def get_product_by_id(self, product_id: int) -> dict[str, Any] | None:
        """Get a product by ID with resilience patterns applied.

        Args:
            product_id: ID of the product.

        Returns:
            Product data dict, or None on failure.
        """
        try:
            async with _bulkhead:
                return await _circuit.call(
                    _retry.execute, self._fetch_product, product_id
                )
        except Exception as e:
            logger.error(
                "All resilience layers failed for product %s: %s", product_id, e
            )
            return None

    async def get_supplier_ids_for_products(
        self, product_ids: list[int]
    ) -> dict[int, int]:
        """Get supplier ID mapping for a batch of product IDs.

        Args:
            product_ids: List of product IDs to look up.

        Returns:
            Dict mapping product_id to supplier_id. Empty on failure.
        """
        url = "/internal/products/suppliers/batch"
        try:
            response = await self._client.post(url, json=product_ids)
            response.raise_for_status()
            data = response.json()
            return {item["product_id"]: item["supplier_id"] for item in data}
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error fetching suppliers for products: %s", e.response.status_code
            )
            return {}
        except httpx.RequestError as e:
            logger.error("Connection error fetching suppliers for products: %s", e)
            return {}

    async def get_vendor_products(
        self, supplier_id: int, page: int = 1, limit: int = 20
    ) -> dict[str, Any] | None:
        """Get paginated vendor products with resilience patterns applied.

        Args:
            supplier_id: ID of the vendor.
            page: Page number.
            limit: Items per page.

        Returns:
            Paginated product data dict, or None on failure.
        """
        try:
            async with _bulkhead:
                return await _circuit.call(
                    _retry.execute,
                    self._fetch_vendor_products,
                    supplier_id,
                    page,
                    limit,
                )
        except Exception as e:
            logger.error(
                "All resilience layers failed for vendor %s products: %s",
                supplier_id,
                e,
            )
            return None


_catalog_client: httpx.AsyncClient | None = None


def init_catalog_http_client() -> None:
    """Initialize the global catalog HTTP client."""
    global _catalog_client
    _catalog_client = httpx.AsyncClient(
        base_url=settings.PRODUCTS_SERVICE_URL.rstrip("/"),
        timeout=httpx.Timeout(5.0),
    )


async def close_catalog_http_client() -> None:
    """Close and clean up the global catalog HTTP client."""
    global _catalog_client
    if _catalog_client:
        await _catalog_client.aclose()
        _catalog_client = None


def get_catalog_http_client() -> CatalogHttpClient:
    """Get the global catalog HTTP client instance.

    Returns:
        A CatalogHttpClient wrapping the global httpx client.
    """
    return CatalogHttpClient(_catalog_client)
