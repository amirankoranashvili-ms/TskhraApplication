"""Unit tests for the verification request RabbitMQ consumer."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select

from src.app.core.constants import VerificationRequestType, VerificationStatus
from src.app.infra.broker.consumer import VerificationConsumer
from src.app.infra.database.models.products import VerificationRequestDb


@pytest.fixture
def consumer():
    return VerificationConsumer(connection=MagicMock())


def _patch_async_session(products_session):
    """Return a patch context that makes async_session() yield the test session."""
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = products_session
    mock_ctx.__aexit__.return_value = False
    return patch(
        "src.app.infra.broker.consumer.async_session",
        return_value=mock_ctx,
    )


class TestVerificationConsumer:
    def test_routing_keys(self, consumer):
        assert consumer.get_routing_keys() == ["vendor.created"]

    @pytest.mark.asyncio
    async def test_creates_seller_verification_request(
        self, consumer, products_session
    ):
        with _patch_async_session(products_session):
            await consumer.handle_message("vendor.created", {"supplier_id": 42})

        result = await products_session.execute(select(VerificationRequestDb))
        vr = result.scalar_one()

        assert vr.request_type == VerificationRequestType.SELLER.value
        assert vr.supplier_id == 42
        assert vr.status == VerificationStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_ignores_negative_supplier_id(self, consumer, products_session):
        with _patch_async_session(products_session):
            await consumer.handle_message("vendor.created", {"supplier_id": -1})

        result = await products_session.execute(select(VerificationRequestDb))
        assert result.scalars().all() == []

    @pytest.mark.asyncio
    async def test_ignores_missing_supplier_id(self, consumer, products_session):
        with _patch_async_session(products_session):
            await consumer.handle_message("vendor.created", {})

        result = await products_session.execute(select(VerificationRequestDb))
        assert result.scalars().all() == []
