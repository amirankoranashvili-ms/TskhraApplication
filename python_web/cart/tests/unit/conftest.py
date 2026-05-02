import uuid

import pytest
from unittest.mock import AsyncMock

from src.app.core.cart.entities import Cart, CartItem, CartStatus
from src.app.core.cart.service import CartService


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def service(mock_repo):
    return CartService(cart_repository=mock_repo)


@pytest.fixture
def user_id():
    return uuid.uuid4()


@pytest.fixture
def active_cart(user_id):
    return Cart(id=uuid.uuid4(), user_id=user_id, items=[], status=CartStatus.ACTIVE)


@pytest.fixture
def cart_with_items(user_id):
    cart_id = uuid.uuid4()
    items = [
        CartItem(
            id=uuid.uuid4(),
            cart_id=cart_id,
            product_id=1,
            quantity=2,
            unit_price=100.0,
            product_title="Item 1",
        ),
        CartItem(
            id=uuid.uuid4(),
            cart_id=cart_id,
            product_id=2,
            quantity=1,
            unit_price=50.0,
            product_title="Item 2",
        ),
    ]
    return Cart(id=cart_id, user_id=user_id, items=items, status=CartStatus.ACTIVE)
