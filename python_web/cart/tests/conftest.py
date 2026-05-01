import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from backend_common.database.base import Base

from src.app.runner.asgi import app
from src.app.infra.auth.auth import get_current_user_id
from src.app.infra.web.dependables import get_db, _get_catalog_facade, _get_publisher

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


class MockCatalogFacade:
    def __init__(self):
        self._products: dict[int, dict] = {}

    def set_product(self, product_id: int, data: dict) -> None:
        self._products[product_id] = data

    async def get_product(self, product_id: int) -> dict:
        return self._products.get(product_id, {})

    async def validate_product_available(self, product_id: int, quantity: int) -> bool:
        product = self._products.get(product_id)
        if not product:
            return False
        return (
            product.get("is_active", True)
            and product.get("stock_quantity", 0) >= quantity
        )


class MockEventPublisher:
    def __init__(self):
        self.published: list[dict] = []

    async def publish(self, routing_key: str, payload: dict) -> None:
        self.published.append({"routing_key": routing_key, "payload": payload})

    async def close(self) -> None:
        pass


@pytest_asyncio.fixture(scope="function")
async def mock_catalog():
    facade = MockCatalogFacade()
    facade.set_product(
        1,
        {
            "id": 1,
            "title": "Test Product",
            "price": 99.99,
            "stock_quantity": 50,
            "is_active": True,
            "image_url": "http://example.com/img.png",
        },
    )
    facade.set_product(
        2,
        {
            "id": 2,
            "title": "Another Product",
            "price": 49.50,
            "stock_quantity": 5,
            "is_active": True,
            "image_url": None,
        },
    )
    return facade


@pytest_asyncio.fixture(scope="function")
async def mock_publisher():
    return MockEventPublisher()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def user_id():
    return uuid4()


@pytest_asyncio.fixture(scope="function")
async def client(db_session, mock_catalog, mock_publisher, user_id):
    async def override_get_db():
        yield db_session

    async def override_get_current_user_id():
        return user_id

    def override_get_catalog_facade():
        return mock_catalog

    def override_get_publisher():
        return mock_publisher

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    app.dependency_overrides[_get_catalog_facade] = override_get_catalog_facade
    app.dependency_overrides[_get_publisher] = override_get_publisher

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
