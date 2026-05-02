import pytest


async def test_get_empty_cart(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0.0
    assert data["status"] == "ACTIVE"


async def test_get_cart_with_items(client):
    await client.post("/items", json={"product_id": 1, "quantity": 2})
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == 1
    assert data["items"][0]["quantity"] == 2
    assert data["total"] == pytest.approx(199.98)
