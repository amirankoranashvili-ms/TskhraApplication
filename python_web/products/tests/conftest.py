import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from uuid import uuid4
from decimal import Decimal

from src.app.runner.asgi import app
from backend_common.database.base import Base
from src.app.infra.database.config import get_db
from src.app.infra.auth.auth import get_current_user_id
from src.app.infra.web.dependables import get_search_repo, get_category_service
from src.app.core.categories.service import CategoryService
from src.app.infra.database.repositories import (
    SqlAlchemyCategoryRepository,
    SqlAlchemyCategoryFieldRepository,
)
from src.app.infra.database.models import (
    BrandDb,
    CategoryDb,
    SupplierDb,
    ProductDb,
)

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class MockSearchRepo:
    async def search_products(self, q, limit, offset, **kwargs):
        return [], 0

    async def index_product(self, product_data):
        pass

    async def index_products_batch(self, products):
        pass

    async def delete_product_document(self, product_id):
        pass

    async def delete_all_documents(self):
        pass


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    mock_user_id = uuid4()

    async def override_get_current_user_id():
        return mock_user_id

    async def override_get_search_repo():
        return MockSearchRepo()

    async def override_get_category_service():
        cat_repo = SqlAlchemyCategoryRepository(db_session)
        field_repo = SqlAlchemyCategoryFieldRepository(db_session)
        return CategoryService(cat_repo, field_repo, cache=None)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[get_search_repo] = override_get_search_repo
    app.dependency_overrides[get_category_service] = override_get_category_service

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, mock_user_id

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def seed_brand(db_session):
    brand = BrandDb(
        name="TestBrand", logo_url="http://example.com/logo.png", is_deleted=False
    )
    db_session.add(brand)
    await db_session.flush()
    await db_session.refresh(brand)
    return brand


@pytest_asyncio.fixture(scope="function")
async def seed_category(db_session):
    category = CategoryDb(
        name="TestCategory",
        slug="test-category",
        image_url="http://example.com/cat.png",
        parent_id=None,
        is_deleted=False,
    )
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    return category


@pytest_asyncio.fixture(scope="function")
async def seed_supplier(db_session):
    supplier = SupplierDb(
        name="TestSupplier", supplier_type="external", is_deleted=False
    )
    db_session.add(supplier)
    await db_session.flush()
    await db_session.refresh(supplier)
    return supplier


@pytest_asyncio.fixture(scope="function")
async def seed_product(db_session, seed_brand, seed_category, seed_supplier):
    product = ProductDb(
        category_id=seed_category.id,
        supplier_id=seed_supplier.id,
        brand_id=seed_brand.id,
        title="Test Product",
        description="A test product description",
        price=Decimal("99.99"),
        cost_price=Decimal("50.00"),
        sku="TEST-SKU-001",
        stock_quantity=10,
        cover_image_url="http://example.com/product.png",
        is_active=True,
        is_deleted=False,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product
