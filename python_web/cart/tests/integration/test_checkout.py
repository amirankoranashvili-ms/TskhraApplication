import pytest


async def test_checkout_success(client, mock_publisher):
    await client.post("/items", json={"product_id": 1, "quantity": 2})
    response = await client.post("/checkout")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CHECKED_OUT"
    assert data["item_count"] == 1
    assert data["total"] == pytest.approx(199.98)
    assert "message" in data
    assert len(mock_publisher.published) == 1
    event = mock_publisher.published[0]
    assert event["routing_key"] == "cart.checkout"
    assert len(event["payload"]["items"]) == 1


async def test_checkout_empty_cart(client):
    await client.get("/")
    response = await client.post("/checkout")
    assert response.status_code == 422


async def test_double_checkout_fails(client):
    await client.post("/items", json={"product_id": 1, "quantity": 1})
    await client.post("/checkout")
    # After checkout, get_or_create_cart creates a new empty cart
    response = await client.post("/checkout")
    assert response.status_code == 422  # empty cart


async def test_new_cart_created_after_checkout(client):
    await client.post("/items", json={"product_id": 1, "quantity": 1})
    first_cart = await client.get("/")
    first_cart_id = first_cart.json()["id"]

    await client.post("/checkout")

    # A new empty cart is created after checkout
    new_cart = await client.get("/")
    assert new_cart.json()["id"] != first_cart_id
    assert new_cart.json()["items"] == []
    assert new_cart.json()["status"] == "ACTIVE"
