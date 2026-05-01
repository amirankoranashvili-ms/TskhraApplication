import uuid

import pytest

from src.app.core.cart.entities import CartItem, CartStatus
from src.app.core.cart.exceptions import (
    CartAlreadyCheckedOutException,
    CartItemNotFoundException,
)


async def test_remove_item(service, mock_repo, active_cart):
    item_id = uuid.uuid4()
    item = CartItem(
        id=item_id,
        cart_id=active_cart.id,
        product_id=1,
        quantity=1,
        unit_price=10.0,
        product_title="X",
    )
    mock_repo.get_item_by_id.return_value = item
    await service.remove_item(active_cart, item_id)
    mock_repo.remove_item.assert_called_once_with(item_id, active_cart.id)


async def test_remove_from_checked_out_raises(service, active_cart):
    active_cart.status = CartStatus.CHECKED_OUT
    with pytest.raises(CartAlreadyCheckedOutException):
        await service.remove_item(active_cart, uuid.uuid4())


async def test_remove_nonexistent_raises(service, mock_repo, active_cart):
    mock_repo.get_item_by_id.return_value = None
    with pytest.raises(CartItemNotFoundException):
        await service.remove_item(active_cart, uuid.uuid4())
