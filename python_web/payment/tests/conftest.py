import os

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("RABBITMQ_URL", "amqp://guest:guest@localhost/")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from backend_common.database.base import Base
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.app.core.payment.entities import PaymentResult, PaymentStatus
from src.app.infra.auth.auth import get_current_user_id
from src.app.infra.database.models import OrderDB, OrderItemDB, PaymentDB
from src.app.infra.web.dependables import get_db, init_payment_deps
from src.app.runner.setup import create_app

TEST_USER_ID: UUID = uuid4()

_test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(_test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def mock_gateway():
    gw = MagicMock()
    gw.charge = AsyncMock(
        return_value=PaymentResult(
            success=True,
            provider_payment_id="test_order_abc123",
            redirect_url="https://pay.keepz.me/test",
            requires_redirect=True,
        )
    )
    gw.check_status = AsyncMock(return_value=PaymentStatus.COMPLETED)
    return gw


@pytest.fixture
def mock_publisher():
    pub = MagicMock()
    pub.publish = AsyncMock()
    return pub


@pytest.fixture
def mock_cache():
    cache = MagicMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    return cache


@pytest_asyncio.fixture
async def client(db_session, mock_gateway, mock_publisher, mock_cache):
    init_payment_deps(
        publisher=mock_publisher,
        payment_gateway=mock_gateway,
        cache_service=mock_cache,
    )

    app: FastAPI = create_app()

    async def _override_get_db():
        yield db_session

    async def _override_get_current_user_id() -> UUID:
        return TEST_USER_ID

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user_id] = _override_get_current_user_id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac, TEST_USER_ID

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seed_order(db_session):
    order = OrderDB(
        id=uuid4(),
        user_id=TEST_USER_ID,
        status="PENDING",
        total_amount=99.99,
    )
    item = OrderItemDB(
        id=uuid4(),
        order_id=order.id,
        entity_id="product-123",
        quantity=2,
        unit_price=49.99,
        product_title="Test Product",
    )
    db_session.add(order)
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(order)
    return order


@pytest_asyncio.fixture
async def seed_payment(db_session, seed_order):
    payment = PaymentDB(
        id=uuid4(),
        order_id=seed_order.id,
        amount=99.99,
        status="PENDING",
        provider_payment_id="test_order_abc123",
    )
    db_session.add(payment)
    await db_session.commit()
    await db_session.refresh(payment)
    return payment
