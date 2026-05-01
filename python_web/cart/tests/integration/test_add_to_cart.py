import pytest


async def test_add_item(client):
    response = await client.post("/items", json={"product_id": 1, "quantity": 3})
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == 1
    assert data["quantity"] == 3
    assert data["unit_price"] == pytest.approx(99.99)
    assert data["product_title"] == "Test Product"
    assert data["subtotal"] == pytest.approx(299.97)


async def test_add_same_product_increments_quantity(client):
    await client.post("/items", json={"product_id": 1, "quantity": 2})
    response = await client.post("/items", json={"product_id": 1, "quantity": 3})
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == 5


async def test_add_multiple_products(client):
    await client.post("/items", json={"product_id": 1, "quantity": 1})
    await client.post("/items", json={"product_id": 2, "quantity": 2})
    response = await client.get("/")
    data = response.json()
    assert len(data["items"]) == 2


async def test_add_nonexistent_product(client):
    response = await client.post("/items", json={"product_id": 999, "quantity": 1})
    assert response.status_code == 422


async def test_add_exceeding_stock(client, mock_catalog):
    mock_catalog.set_product(
        10,
        {
            "id": 10,
            "title": "Low Stock",
            "price": 10.0,
            "stock_quantity": 2,
            "is_active": True,
        },
    )
    response = await client.post("/items", json={"product_id": 10, "quantity": 5})
    assert response.status_code == 422


async def test_add_inactive_product(client, mock_catalog):
    mock_catalog.set_product(
        20,
        {
            "id": 20,
            "title": "Inactive",
            "price": 5.0,
            "stock_quantity": 100,
            "is_active": False,
        },
    )
    response = await client.post("/items", json={"product_id": 20, "quantity": 1})
    assert response.status_code == 422


async def test_add_same_product_exceeding_stock_incrementally(client, mock_catalog):
    mock_catalog.set_product(
        30,
        {
            "id": 30,
            "title": "Limited Stock",
            "price": 25.0,
            "stock_quantity": 2,
            "is_active": True,
            "image_url": None,
        },
    )
    response = await client.post("/items", json={"product_id": 30, "quantity": 1})
    assert response.status_code == 201

    response = await client.post("/items", json={"product_id": 30, "quantity": 2})
    assert response.status_code == 422


async def test_add_zero_quantity_rejected(client):
    response = await client.post("/items", json={"product_id": 1, "quantity": 0})
    assert response.status_code == 422


async def test_add_negative_quantity_rejected(client):
    response = await client.post("/items", json={"product_id": 1, "quantity": -1})
    assert response.status_code == 422
