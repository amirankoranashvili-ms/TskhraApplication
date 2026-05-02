import uuid

import pytest

from src.app.core.cart.entities import CartItem, CartStatus
from src.app.core.cart.exceptions import (
    CartAlreadyCheckedOutException,
    CartItemNotFoundException,
    InvalidQuantityException,
)


async def test_update_quantity(service, mock_repo, active_cart):
    item = CartItem(
        id=uuid.uuid4(),
        cart_id=active_cart.id,
        product_id=1,
        quantity=2,
        unit_price=10.0,
        product_title="X",
    )
    mock_repo.get_item_by_id.return_value = item
    mock_repo.update_item.return_value = item

    await service.update_quantity(active_cart, item.id, 5)
    assert item.quantity == 5


async def test_update_zero_quantity_raises(service, active_cart):
    with pytest.raises(InvalidQuantityException):
        await service.update_quantity(active_cart, uuid.uuid4(), 0)


async def test_update_checked_out_cart_raises(service, active_cart):
    active_cart.status = CartStatus.CHECKED_OUT
    with pytest.raises(CartAlreadyCheckedOutException):
        await service.update_quantity(active_cart, uuid.uuid4(), 1)


async def test_update_nonexistent_item_raises(service, mock_repo, active_cart):
    mock_repo.get_item_by_id.return_value = None
    with pytest.raises(CartItemNotFoundException):
        await service.update_quantity(active_cart, uuid.uuid4(), 1)
