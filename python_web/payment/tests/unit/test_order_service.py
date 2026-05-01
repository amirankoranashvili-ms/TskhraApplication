from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.app.core.order.entities import Order, OrderItem, OrderStatus
from src.app.core.order.exceptions import (
    OrderAccessDeniedException,
    OrderNotFoundException,
    OrderNotPayableException,
)
from src.app.core.order.service import OrderService


def make_mock_repo():
    return AsyncMock()


def make_order_item(order_id):
    return OrderItem(
        id=uuid4(),
        order_id=order_id,
        entity_id="ent_001",
        quantity=2,
        unit_price=49.99,
        product_title="Test Product",
    )


def make_order(user_id=None, status=OrderStatus.PENDING):
    oid = uuid4()
    uid = user_id or uuid4()
    return Order(
        id=oid,
        user_id=uid,
        items=[make_order_item(oid)],
        status=status,
        total_amount=99.98,
    )


@pytest.fixture
def repo():
    return make_mock_repo()


@pytest.fixture
def service(repo):
    return OrderService(order_repository=repo)


@pytest.mark.asyncio
async def test_create_order_from_checkout(service, repo):
    user_id = uuid4()
    items = [
        {
            "entity_id": "ent_001",
            "quantity": 1,
            "unit_price": Decimal("29.99"),
            "product_title": "Book A",
        },
        {
            "entity_id": "ent_002",
            "quantity": 2,
            "unit_price": Decimal("14.99"),
            "product_title": "Book B",
        },
    ]
    total = Decimal("59.97")

    expected_order = make_order(user_id=user_id)
    repo.create.return_value = expected_order

    result = await service.create_order_from_checkout(user_id, items, total)

    repo.create.assert_awaited_once()
    created_arg: Order = repo.create.call_args[0][0]
    assert created_arg.user_id == user_id
    assert len(created_arg.items) == 2
    assert created_arg.status == OrderStatus.PENDING
    assert created_arg.total_amount == total
    assert result is expected_order


@pytest.mark.asyncio
async def test_get_order_not_found(service, repo):
    repo.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundException):
        await service.get_order(uuid4())


@pytest.mark.asyncio
async def test_get_order_enforces_ownership(service, repo):
    order = make_order()
    repo.get_by_id.return_value = order

    wrong_user = uuid4()
    assert wrong_user != order.user_id

    with pytest.raises(OrderAccessDeniedException):
        await service.get_order(order.id, user_id=wrong_user)


@pytest.mark.asyncio
async def test_get_order_no_ownership_check(service, repo):
    order = make_order()
    repo.get_by_id.return_value = order

    result = await service.get_order(order.id, user_id=None)

    assert result is order


@pytest.mark.asyncio
async def test_get_order_history_paginated(service, repo):
    user_id = uuid4()
    orders = [make_order(user_id=user_id) for _ in range(3)]
    total = 10
    repo.get_by_user_id.return_value = (orders, total)

    result_orders, result_total = await service.get_order_history(
        user_id, page=2, limit=3
    )

    repo.get_by_user_id.assert_awaited_once_with(user_id, 3, 3)
    assert result_orders is orders
    assert result_total == total


@pytest.mark.asyncio
async def test_mark_as_paid_success(service, repo):
    order = make_order(status=OrderStatus.PENDING)
    paid_order = make_order(user_id=order.user_id, status=OrderStatus.PAID)
    paid_order = paid_order.model_copy(update={"id": order.id})

    repo.get_by_id.return_value = order
    repo.update_status.return_value = paid_order

    result = await service.mark_as_paid(order.id)

    repo.update_status.assert_awaited_once_with(order.id, OrderStatus.PAID)
    assert result.status == OrderStatus.PAID


@pytest.mark.asyncio
async def test_mark_as_paid_already_paid(service, repo):
    order = make_order(status=OrderStatus.PAID)
    repo.get_by_id.return_value = order

    with pytest.raises(OrderNotPayableException):
        await service.mark_as_paid(order.id)

    repo.update_status.assert_not_awaited()


@pytest.mark.asyncio
async def test_mark_as_paid_not_found(service, repo):
    repo.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundException):
        await service.mark_as_paid(uuid4())


@pytest.mark.asyncio
async def test_update_order_status(service, repo):
    order_id = uuid4()
    updated_order = make_order(status=OrderStatus.SHIPPED)
    updated_order = updated_order.model_copy(update={"id": order_id})
    repo.update_status.return_value = updated_order

    result = await service.update_order_status(order_id, OrderStatus.SHIPPED)

    repo.update_status.assert_awaited_once_with(order_id, OrderStatus.SHIPPED)
    assert result is updated_order
