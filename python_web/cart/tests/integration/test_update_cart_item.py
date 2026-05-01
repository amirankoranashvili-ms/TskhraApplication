import pytest


async def test_update_quantity(client):
    add_resp = await client.post("/items", json={"product_id": 1, "quantity": 2})
    item_id = add_resp.json()["id"]

    response = await client.put(f"/items/{item_id}", json={"quantity": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 5
    assert data["subtotal"] == pytest.approx(99.99 * 5)


async def test_update_nonexistent_item(client):
    await client.get("/")
    response = await client.put(
        "/items/00000000-0000-0000-0000-000000000001",
        json={"quantity": 1},
    )
    assert response.status_code == 404


async def test_update_exceeding_stock(client, mock_catalog):
    mock_catalog.set_product(
        2,
        {
            "id": 2,
            "title": "Limited",
            "price": 10.0,
            "stock_quantity": 3,
            "is_active": True,
        },
    )
    add_resp = await client.post("/items", json={"product_id": 2, "quantity": 1})
    item_id = add_resp.json()["id"]

    response = await client.put(f"/items/{item_id}", json={"quantity": 10})
    assert response.status_code == 422


async def test_update_zero_quantity_rejected(client):
    add_resp = await client.post("/items", json={"product_id": 1, "quantity": 1})
    item_id = add_resp.json()["id"]

    response = await client.put(f"/items/{item_id}", json={"quantity": 0})
    assert response.status_code == 422
