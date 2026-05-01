from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.app.core.facades.order_facade import OrderFacade
from src.app.core.order.entities import Order, OrderItem, OrderStatus
from src.app.core.payment.entities import Payment, PaymentStatus
from src.app.core.payment.exceptions import PaymentFailedException


def make_order(status: OrderStatus = OrderStatus.PENDING) -> Order:
    order_id = uuid4()
    return Order(
        id=order_id,
        user_id=uuid4(),
        items=[
            OrderItem(
                id=uuid4(),
                order_id=order_id,
                entity_id="p-1",
                quantity=2,
                unit_price=50.0,
                product_title="Product",
            )
        ],
        status=status,
        total_amount=100.0,
    )


def make_payment(status: PaymentStatus, redirect_url: str | None = None) -> Payment:
    return Payment(
        id=uuid4(),
        order_id=uuid4(),
        amount=100.0,
        status=status,
        redirect_url=redirect_url,
    )


@pytest.fixture
def order_service():
    svc = AsyncMock()
    return svc


@pytest.fixture
def payment_service():
    svc = AsyncMock()
    return svc


@pytest.fixture
def publisher():
    pub = AsyncMock()
    return pub


@pytest.fixture
def facade(order_service, payment_service, publisher):
    return OrderFacade(
        order_service=order_service,
        payment_service=payment_service,
        publisher=publisher,
    )


@pytest.mark.asyncio
async def test_process_payment_pending_redirect(
    facade, order_service, payment_service, publisher
):
    order = make_order()
    payment = make_payment(
        PaymentStatus.PENDING, redirect_url="https://pay.example.com/redirect"
    )
    order_service.get_order.return_value = order
    payment_service.process_payment.return_value = (
        payment,
        "https://pay.example.com/redirect",
    )

    result_order, result_url = await facade.process_payment_for_order(
        order_id=order.id, user_id=order.user_id
    )

    publisher.publish.assert_not_called()
    order_service.mark_as_paid.assert_not_called()
    assert result_order is order
    assert result_url == "https://pay.example.com/redirect"


@pytest.mark.asyncio
async def test_process_payment_completed_immediately(
    facade, order_service, payment_service, publisher
):
    order = make_order()
    payment = make_payment(PaymentStatus.COMPLETED)
    paid_order = make_order(status=OrderStatus.PAID)
    order_service.get_order.return_value = order
    payment_service.process_payment.return_value = (payment, None)
    order_service.mark_as_paid.return_value = paid_order

    result_order, result_url = await facade.process_payment_for_order(
        order_id=order.id, user_id=order.user_id
    )

    publisher.publish.assert_awaited_once()
    call_kwargs = publisher.publish.call_args
    assert call_kwargs.kwargs["routing_key"] == "payment.completed"
    order_service.mark_as_paid.assert_awaited_once_with(order.id)
    assert result_order is paid_order
    assert result_url is None


@pytest.mark.asyncio
async def test_process_payment_failure(
    facade, order_service, payment_service, publisher
):
    order = make_order()
    order_service.get_order.return_value = order
    payment_service.process_payment.side_effect = PaymentFailedException()

    with pytest.raises(PaymentFailedException):
        await facade.process_payment_for_order(order_id=order.id, user_id=order.user_id)

    publisher.publish.assert_awaited_once()
    call_kwargs = publisher.publish.call_args
    assert call_kwargs.kwargs["routing_key"] == "payment.failed"
    order_service.mark_as_paid.assert_not_called()


@pytest.mark.asyncio
async def test_verify_payment_marks_paid_when_completed(
    facade, order_service, payment_service, publisher
):
    order = make_order(status=OrderStatus.PENDING)
    payment = make_payment(PaymentStatus.COMPLETED)
    paid_order = make_order(status=OrderStatus.PAID)
    order_service.get_order.return_value = order
    payment_service.verify_payment.return_value = payment
    order_service.mark_as_paid.return_value = paid_order

    result_order, result_url = await facade.verify_payment(
        order_id=order.id, user_id=order.user_id
    )

    publisher.publish.assert_awaited_once()
    call_kwargs = publisher.publish.call_args
    assert call_kwargs.kwargs["routing_key"] == "payment.completed"
    order_service.mark_as_paid.assert_awaited_once_with(order.id)
    assert result_order is paid_order
    assert result_url is None


@pytest.mark.asyncio
async def test_verify_payment_already_paid_order(
    facade, order_service, payment_service, publisher
):
    order = make_order(status=OrderStatus.PAID)
    payment = make_payment(PaymentStatus.COMPLETED)
    order_service.get_order.return_value = order
    payment_service.verify_payment.return_value = payment

    result_order, result_url = await facade.verify_payment(
        order_id=order.id, user_id=order.user_id
    )

    publisher.publish.assert_not_called()
    order_service.mark_as_paid.assert_not_called()
    assert result_order is order


@pytest.mark.asyncio
async def test_verify_payment_still_pending(
    facade, order_service, payment_service, publisher
):
    order = make_order(status=OrderStatus.PENDING)
    payment = make_payment(PaymentStatus.PENDING)
    order_service.get_order.return_value = order
    payment_service.verify_payment.return_value = payment

    result_order, result_url = await facade.verify_payment(
        order_id=order.id, user_id=order.user_id
    )

    publisher.publish.assert_not_called()
    order_service.mark_as_paid.assert_not_called()
    assert result_order is order


@pytest.mark.asyncio
async def test_create_order_from_checkout(facade, order_service):
    user_id = uuid4()
    items = [
        {"entity_id": "p-1", "quantity": 1, "unit_price": 99.0, "product_title": "P"}
    ]
    created_order = make_order()
    order_service.create_order_from_checkout.return_value = created_order

    result = await facade.create_order_from_checkout(
        user_id=user_id, items=items, total_amount=99.0
    )

    order_service.create_order_from_checkout.assert_awaited_once_with(
        user_id=user_id, items=items, total_amount=99.0
    )
    assert result is created_order
