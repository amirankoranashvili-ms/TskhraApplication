from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.app.core.payment.entities import Payment, PaymentResult, PaymentStatus
from src.app.core.payment.exceptions import (
    PaymentFailedException,
    PaymentNotFoundException,
)
from src.app.core.payment.service import PaymentService


def make_mock_repo():
    return AsyncMock()


def make_mock_gateway():
    return AsyncMock()


def make_mock_cache(cached_url=None):
    cache = MagicMock()
    cache.get = AsyncMock(return_value=cached_url)
    cache.set = AsyncMock()
    return cache


def make_payment(status=PaymentStatus.PENDING, provider_id=None):
    return Payment(
        id=uuid4(),
        order_id=uuid4(),
        amount=99.99,
        status=status,
        provider_payment_id=provider_id,
    )


@pytest.fixture
def repo():
    return make_mock_repo()


@pytest.fixture
def gateway():
    return make_mock_gateway()


@pytest.fixture
def cache():
    return make_mock_cache()


@pytest.fixture
def service(repo, gateway, cache):
    return PaymentService(payment_repository=repo, payment_gateway=gateway, cache=cache)


@pytest.mark.asyncio
async def test_process_payment_success_redirect(service, repo, gateway, cache):
    order_id = uuid4()
    redirect = "https://pay.example.com/session/abc"
    provider_id = "prov_123"

    repo.get_by_order_id.return_value = None
    created = make_payment(status=PaymentStatus.PENDING)
    repo.create.return_value = created

    updated = make_payment(status=PaymentStatus.PENDING, provider_id=provider_id)
    repo.update_status.return_value = updated

    gateway.charge.return_value = PaymentResult(
        success=True,
        requires_redirect=True,
        provider_payment_id=provider_id,
        redirect_url=redirect,
    )

    payment, returned_url = await service.process_payment(order_id, 99.99)

    assert payment.status == PaymentStatus.PENDING
    assert returned_url == redirect
    repo.update_status.assert_awaited_once_with(
        created.id, PaymentStatus.PENDING, provider_id
    )
    cache.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_payment_returns_existing_pending_from_cache(
    service, repo, gateway, cache
):
    cached_url = "https://pay.example.com/x"
    cache.get.return_value = cached_url
    existing = make_payment(status=PaymentStatus.PENDING)
    repo.get_by_order_id.return_value = existing

    payment, url = await service.process_payment(existing.order_id, 99.99)

    assert payment is existing
    assert url == cached_url
    gateway.charge.assert_not_awaited()
    repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_payment_refreshes_url_on_cache_miss(
    service, repo, gateway, cache
):
    cache.get.return_value = None  # cache expired
    existing = make_payment(status=PaymentStatus.PENDING)
    repo.get_by_order_id.return_value = existing
    repo.update_status.return_value = existing

    new_url = "https://pay.example.com/new"
    gateway.charge.return_value = PaymentResult(
        success=True,
        requires_redirect=True,
        provider_payment_id="prov_new",
        redirect_url=new_url,
    )

    payment, url = await service.process_payment(existing.order_id, 99.99)

    assert payment is existing
    assert url == new_url
    gateway.charge.assert_awaited_once()
    cache.set.assert_awaited_once()
    repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_payment_no_existing_then_creates(service, repo, gateway):
    order_id = uuid4()
    repo.get_by_order_id.return_value = None

    created = make_payment(status=PaymentStatus.PENDING)
    repo.create.return_value = created

    updated = make_payment(status=PaymentStatus.COMPLETED, provider_id="prov_456")
    repo.update_status.return_value = updated

    gateway.charge.return_value = PaymentResult(
        success=True,
        requires_redirect=False,
        provider_payment_id="prov_456",
    )

    payment, url = await service.process_payment(order_id, 50.0)

    repo.create.assert_awaited_once()
    gateway.charge.assert_awaited_once()
    assert payment is updated


@pytest.mark.asyncio
async def test_process_payment_gateway_failure(service, repo, gateway):
    order_id = uuid4()
    repo.get_by_order_id.return_value = None

    created = make_payment(status=PaymentStatus.PENDING)
    repo.create.return_value = created
    repo.update_status.return_value = None

    gateway.charge.return_value = PaymentResult(
        success=False,
        error_message="Card declined",
    )

    with pytest.raises(PaymentFailedException):
        await service.process_payment(order_id, 99.99)

    repo.update_status.assert_awaited_once_with(created.id, PaymentStatus.FAILED)


@pytest.mark.asyncio
async def test_process_payment_immediate_success(service, repo, gateway):
    order_id = uuid4()
    repo.get_by_order_id.return_value = None

    created = make_payment(status=PaymentStatus.PENDING)
    repo.create.return_value = created

    updated = make_payment(status=PaymentStatus.COMPLETED, provider_id="prov_789")
    repo.update_status.return_value = updated

    gateway.charge.return_value = PaymentResult(
        success=True,
        requires_redirect=False,
        provider_payment_id="prov_789",
    )

    payment, url = await service.process_payment(order_id, 99.99)

    assert payment.status == PaymentStatus.COMPLETED
    assert url is None
    repo.update_status.assert_awaited_once_with(
        created.id, PaymentStatus.COMPLETED, "prov_789"
    )


@pytest.mark.asyncio
async def test_verify_payment_already_completed(service, repo, gateway):
    completed = make_payment(status=PaymentStatus.COMPLETED, provider_id="prov_done")
    repo.get_by_order_id.return_value = completed

    result = await service.verify_payment(completed.order_id)

    assert result is completed
    gateway.check_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_verify_payment_no_provider_id(service, repo, gateway):
    pending = make_payment(status=PaymentStatus.PENDING, provider_id=None)
    repo.get_by_order_id.return_value = pending

    result = await service.verify_payment(pending.order_id)

    assert result is pending
    gateway.check_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_verify_payment_updates_status(service, repo, gateway):
    pending = make_payment(status=PaymentStatus.PENDING, provider_id="prov_abc")
    repo.get_by_order_id.return_value = pending

    completed_payment = make_payment(
        status=PaymentStatus.COMPLETED, provider_id="prov_abc"
    )
    repo.update_status.return_value = completed_payment

    gateway.check_status.return_value = PaymentStatus.COMPLETED

    result = await service.verify_payment(pending.order_id)

    repo.update_status.assert_awaited_once_with(pending.id, PaymentStatus.COMPLETED)
    assert result is completed_payment


@pytest.mark.asyncio
async def test_verify_payment_not_found(service, repo, gateway):
    repo.get_by_order_id.return_value = None

    with pytest.raises(PaymentNotFoundException):
        await service.verify_payment(uuid4())

    gateway.check_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_payment_by_order_none(service, repo):
    repo.get_by_order_id.return_value = None

    result = await service.get_payment_by_order(uuid4())

    assert result is None
