import pytest

from src.app.core.cart.entities import CartStatus
from src.app.core.cart.exceptions import (
    CartAlreadyCheckedOutException,
    CartEmptyException,
)


def test_calculate_total_empty_cart(service, active_cart):
    assert service.calculate_total(active_cart) == 0.0


def test_calculate_total_with_items(service, cart_with_items):
    total = service.calculate_total(cart_with_items)
    assert total == pytest.approx(250.0)


async def test_checkout_success(service, mock_repo, cart_with_items):
    mock_repo.update.return_value = cart_with_items
    await service.checkout_cart(cart_with_items)
    assert cart_with_items.status == CartStatus.CHECKED_OUT
    mock_repo.update.assert_called_once()


async def test_checkout_already_checked_out_raises(service, active_cart):
    active_cart.status = CartStatus.CHECKED_OUT
    with pytest.raises(CartAlreadyCheckedOutException):
        await service.checkout_cart(active_cart)


async def test_checkout_empty_cart_raises(service, active_cart):
    with pytest.raises(CartEmptyException):
        await service.checkout_cart(active_cart)


async def test_clear_cart(service, mock_repo, active_cart):
    await service.clear_cart(active_cart)
    mock_repo.clear_items.assert_called_once_with(active_cart.id)
