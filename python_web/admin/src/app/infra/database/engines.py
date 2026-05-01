from backend_common.database.engine import create_engine

from src.app.core.config import settings

products_engine = create_engine(
    settings.PRODUCTS_DATABASE_URL, pool_size=5, max_overflow=10
)
vendor_engine = create_engine(
    settings.VENDOR_DATABASE_URL, pool_size=5, max_overflow=10
)
