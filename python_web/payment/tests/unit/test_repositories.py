from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.order.entities import Order, OrderItem, OrderStatus
from src.app.core.payment.entities import Payment, PaymentStatus
from src.app.infra.database.repositories import (
    SqlAlchemyOrderRepository,
    SqlAlchemyPaymentRepository,
)


def make_order(user_id=None) -> Order:
    order_id = uuid4()
    return Order(
        id=order_id,
        user_id=user_id or uuid4(),
        items=[
            OrderItem(
                id=uuid4(),
                order_id=order_id,
                entity_id="p-1",
                quantity=1,
                unit_price=10.0,
                product_title="P",
            )
        ],
        status=OrderStatus.PENDING,
        total_amount=10.0,
    )


def make_payment(order_id=None) -> Payment:
    return Payment(
        id=uuid4(),
        order_id=order_id or uuid4(),
        amount=10.0,
        status=PaymentStatus.PENDING,
    )


@pytest.mark.asyncio
async def test_create_order_and_get_by_id(db_session: AsyncSession):
    repo = SqlAlchemyOrderRepository(db_session)
    order_id = uuid4()
    order = Order(
        id=order_id,
        user_id=uuid4(),
        items=[
            OrderItem(
                id=uuid4(),
                order_id=order_id,
                entity_id="p-1",
                quantity=2,
                unit_price=5.0,
                product_title="Alpha",
            ),
            OrderItem(
                id=uuid4(),
                order_id=order_id,
                entity_id="p-2",
                quantity=1,
                unit_price=20.0,
                product_title="Beta",
            ),
        ],
        status=OrderStatus.PENDING,
        total_amount=30.0,
    )

    created = await repo.create(order)
    fetched = await repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == order_id
    assert fetched.total_amount == 30.0
    assert len(fetched.items) == 2
    entity_ids = {item.entity_id for item in fetched.items}
    assert entity_ids == {"p-1", "p-2"}


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session: AsyncSession):
    repo = SqlAlchemyOrderRepository(db_session)
    result = await repo.get_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_get_by_user_id_paginated(db_session: AsyncSession):
    repo = SqlAlchemyOrderRepository(db_session)
    user_id = uuid4()

    for _ in range(3):
        await repo.create(make_order(user_id=user_id))

    orders, total = await repo.get_by_user_id(user_id, offset=0, limit=2)

    assert total == 3
    assert len(orders) == 2


@pytest.mark.asyncio
async def test_update_status(db_session: AsyncSession):
    repo = SqlAlchemyOrderRepository(db_session)
    order = make_order()
    created = await repo.create(order)
    assert created.status == OrderStatus.PENDING

    updated = await repo.update_status(created.id, OrderStatus.PAID)

    assert updated is not None
    assert updated.status == OrderStatus.PAID


@pytest.mark.asyncio
async def test_create_payment_and_get_by_order_id(db_session: AsyncSession):
    order_repo = SqlAlchemyOrderRepository(db_session)
    pay_repo = SqlAlchemyPaymentRepository(db_session)

    order = await order_repo.create(make_order())
    payment = make_payment(order_id=order.id)
    created = await pay_repo.create(payment)

    fetched = await pay_repo.get_by_order_id(order.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.order_id == order.id
    assert fetched.amount == 10.0
    assert fetched.status == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_get_by_order_id_not_found(db_session: AsyncSession):
    repo = SqlAlchemyPaymentRepository(db_session)
    result = await repo.get_by_order_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_get_by_provider_id(db_session: AsyncSession):
    order_repo = SqlAlchemyOrderRepository(db_session)
    pay_repo = SqlAlchemyPaymentRepository(db_session)

    order = await order_repo.create(make_order())
    payment = Payment(
        id=uuid4(),
        order_id=order.id,
        amount=10.0,
        status=PaymentStatus.COMPLETED,
        provider_payment_id="prov-abc-123",
    )
    created = await pay_repo.create(payment)
    await pay_repo.update_status(
        created.id, PaymentStatus.COMPLETED, provider_payment_id="prov-abc-123"
    )

    fetched = await pay_repo.get_by_provider_id("prov-abc-123")

    assert fetched is not None
    assert fetched.provider_payment_id == "prov-abc-123"


@pytest.mark.asyncio
async def test_update_status_sets_provider_id(db_session: AsyncSession):
    order_repo = SqlAlchemyOrderRepository(db_session)
    pay_repo = SqlAlchemyPaymentRepository(db_session)

    order = await order_repo.create(make_order())
    payment = make_payment(order_id=order.id)
    created = await pay_repo.create(payment)

    updated = await pay_repo.update_status(
        created.id,
        PaymentStatus.COMPLETED,
        provider_payment_id="prov-xyz-999",
    )

    assert updated is not None
    assert updated.provider_payment_id == "prov-xyz-999"
    assert updated.status == PaymentStatus.COMPLETED

    fetched = await pay_repo.get_by_order_id(order.id)
    assert fetched.provider_payment_id == "prov-xyz-999"
