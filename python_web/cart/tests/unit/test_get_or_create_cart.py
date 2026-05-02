import uuid

from src.app.core.cart.entities import Cart, CartStatus


async def test_returns_existing_cart(service, mock_repo, active_cart, user_id):
    mock_repo.get_active_cart_by_user.return_value = active_cart
    result = await service.get_or_create_cart(user_id)
    assert result == active_cart
    mock_repo.create.assert_not_called()


async def test_creates_new_cart_when_none_exists(service, mock_repo, user_id):
    mock_repo.get_active_cart_by_user.return_value = None
    mock_repo.create.return_value = Cart(
        id=uuid.uuid4(),
        user_id=user_id,
        items=[],
        status=CartStatus.ACTIVE,
    )
    result = await service.get_or_create_cart(user_id)
    assert result.user_id == user_id
    assert result.status == CartStatus.ACTIVE
    mock_repo.create.assert_called_once()
