from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.app.infra.database.engines import (
    products_engine,
    vendor_engine,
)
from src.app.infra.database.models.products import (
    BrandDb,
    CategoryDb,
    CategoryFieldDb,
    FieldDb,
    FieldGroupDb,
    FieldOptionDb,
    PlatformSellerDb,
    ProductDb,
    ProductFieldValueDb,
    ProductImageDb,
    SupplierDb,
    VerificationRequestDb,
)
from src.app.infra.database.models.vendor import VendorSellerDb

_PRODUCTS_MODELS = frozenset(
    [
        FieldGroupDb,
        FieldDb,
        FieldOptionDb,
        CategoryFieldDb,
        CategoryDb,
        SupplierDb,
        BrandDb,
        ProductImageDb,
        ProductDb,
        ProductFieldValueDb,
        PlatformSellerDb,
        VerificationRequestDb,
    ]
)
_VENDOR_MODELS = frozenset([VendorSellerDb])


class RoutingSession(orm.Session):
    def get_bind(self, mapper=None, **kwargs):
        if mapper is not None:
            cls = mapper.class_
            if cls in _VENDOR_MODELS:
                return vendor_engine.sync_engine
        return products_engine.sync_engine


async_session = async_sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
    expire_on_commit=False,
)
