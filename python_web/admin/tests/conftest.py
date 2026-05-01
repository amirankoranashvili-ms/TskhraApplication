"""Shared fixtures for the admin service test suite."""

import os

# Must be set before any app module imports to satisfy Settings().
os.environ.setdefault("AUTH_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("PROFILE_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("LISTING_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("PRODUCTS_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("VENDOR_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ADMIN_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ADMIN_PASSWORD", "test-password")

# Patch problematic modules BEFORE they're imported by test files.
import sys
from unittest.mock import MagicMock

# 1) python-magic crashes on this Windows env (msys-magic-1.dll incompatibility).
#    Mock the storage.validation module to avoid importing it.
_mock_validation = MagicMock()
_mock_validation.MIME_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
sys.modules.setdefault("backend_common.storage.validation", _mock_validation)

# 2) backend_common.create_engine passes pool_size / connect_args
#    that are PostgreSQL-only and crash with SQLite.
import backend_common.database.engine as _engine_mod

_real_create_engine = _engine_mod.create_engine


def _test_create_engine(*_args, **_kwargs):
    engine = MagicMock()
    engine.sync_engine = MagicMock()
    return engine


_engine_mod.create_engine = _test_create_engine

# ── Now safe to import app modules ──────────────────────────────────────
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.app.core.constants import VerificationRequestType, VerificationStatus
from src.app.infra.database.base import Base
from src.app.infra.database.models.products import (
    BrandDb,
    CategoryDb,
    PlatformSellerDb,
    ProductDb,
    SupplierDb,
    VerificationRequestDb,
)

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DB_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def products_session():
    """Provide a clean products DB session backed by in-memory SQLite."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSession() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
def vendor_session():
    """Mock vendor DB session (VendorSellerDb uses PgUUID, incompatible with SQLite)."""
    mock = AsyncMock(spec=AsyncSession)
    mock.commit = AsyncMock()
    mock.execute = AsyncMock()
    return mock


@pytest_asyncio.fixture
async def seed_data(products_session):
    """Create the minimum entity graph needed for verification tests."""
    category = CategoryDb(name="TestCat", slug="test-cat", is_deleted=False)
    brand = BrandDb(name="TestBrand", is_deleted=False)
    supplier = SupplierDb(name="TestSupplier", supplier_type="local", is_deleted=False)
    products_session.add_all([category, brand, supplier])
    await products_session.flush()

    product = ProductDb(
        category_id=category.id,
        supplier_id=supplier.id,
        brand_id=brand.id,
        title="Test Product",
        price=Decimal("10.00"),
        cost_price=Decimal("5.00"),
        sku="TEST-001",
        stock_quantity=1,
        is_active=False,
        is_deleted=False,
    )
    seller = PlatformSellerDb(
        supplier_id=supplier.id,
        user_id="user-123",
        identification_number="ID-001",
        legal_address="Test Address",
        is_active=False,
    )
    products_session.add_all([product, seller])
    await products_session.flush()

    return {
        "category": category,
        "brand": brand,
        "supplier": supplier,
        "product": product,
        "seller": seller,
    }


@pytest_asyncio.fixture
async def pending_product_request(products_session, seed_data):
    """Insert a pending product verification request."""
    vr = VerificationRequestDb(
        request_type=VerificationRequestType.PRODUCT.value,
        status=VerificationStatus.PENDING.value,
        supplier_id=seed_data["supplier"].id,
        product_id=seed_data["product"].id,
    )
    products_session.add(vr)
    await products_session.commit()
    return vr


@pytest_asyncio.fixture
async def pending_seller_request(products_session, seed_data):
    """Insert a pending seller verification request."""
    vr = VerificationRequestDb(
        request_type=VerificationRequestType.SELLER.value,
        status=VerificationStatus.PENDING.value,
        supplier_id=seed_data["supplier"].id,
    )
    products_session.add(vr)
    await products_session.commit()
    return vr
