import uuid

import pytest

from src.app.core.cart.entities import CartItem, CartStatus
from src.app.core.cart.exceptions import (
    CartAlreadyCheckedOutException,
    InvalidQuantityException,
)


async def test_add_new_item(service, mock_repo, active_cart):
    mock_repo.get_item_by_product.return_value = None
    expected = CartItem(
        id=uuid.uuid4(),
        cart_id=active_cart.id,
        product_id=1,
        quantity=3,
        unit_price=99.99,
        product_title="Test",
    )
    mock_repo.add_item.return_value = expected

    result = await service.add_item(
        active_cart,
        product_id=1,
        quantity=3,
        unit_price=99.99,
        product_title="Test",
    )
    assert result == expected
    mock_repo.add_item.assert_called_once()


async def test_add_existing_product_increments_quantity(
    service, mock_repo, active_cart
):
    existing = CartItem(
        id=uuid.uuid4(),
        cart_id=active_cart.id,
        product_id=1,
        quantity=2,
        unit_price=50.0,
        product_title="Existing",
    )
    mock_repo.get_item_by_product.return_value = existing
    mock_repo.update_item.return_value = existing

    await service.add_item(
        active_cart,
        product_id=1,
        quantity=3,
        unit_price=55.0,
        product_title="Existing",
    )
    assert existing.quantity == 5
    assert existing.unit_price == 55.0
    mock_repo.update_item.assert_called_once()


async def test_add_zero_quantity_raises(service, active_cart):
    with pytest.raises(InvalidQuantityException):
        await service.add_item(
            active_cart,
            product_id=1,
            quantity=0,
            unit_price=10.0,
            product_title="X",
        )


async def test_add_to_checked_out_cart_raises(service, active_cart):
    active_cart.status = CartStatus.CHECKED_OUT
    with pytest.raises(CartAlreadyCheckedOutException):
        await service.add_item(
            active_cart,
            product_id=1,
            quantity=1,
            unit_price=10.0,
            product_title="X",
        )
