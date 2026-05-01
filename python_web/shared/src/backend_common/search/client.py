"""Meilisearch client factory.

Provides a convenience function for creating an async Meilisearch client.
"""

from meilisearch_python_sdk import AsyncClient


def create_search_client(url: str, api_key: str) -> AsyncClient:
    """Create an async Meilisearch client.

    Args:
        url: The Meilisearch server URL (e.g. ``http://localhost:7700``).
        api_key: The API key for authentication.

    Returns:
        A configured async ``Meilisearch`` client instance.
    """
    return AsyncClient(url, api_key)