"""Redis client configuration.

Creates and exposes a shared Redis client instance for caching
within the products service.
"""

from backend_common.cache.client import create_redis_client
from src.app.core.config import settings

redis_client = create_redis_client(settings.REDIS_URL)
