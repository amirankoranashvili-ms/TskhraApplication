from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_create_order_internal_success(client):
    ac, _ = client
    payload = {
        "user_id": str(uuid4()),
        "items": [
            {
                "entity_id": "product-abc",
                "quantity": 2,
                "unit_price": 49.99,
                "product_title": "Test Item",
            }
        ],
        "total_amount": 99.98,
    }
    response = await ac.post("/internal/orders", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "order_id" in data
    # verify it's a valid UUID string
    uuid4_from_response = data["order_id"]
    assert len(uuid4_from_response) == 36
    assert uuid4_from_response.count("-") == 4


@pytest.mark.asyncio
async def test_create_order_internal_missing_user_id(client):
    ac, _ = client
    payload = {
        "items": [
            {
                "entity_id": "product-abc",
                "quantity": 1,
                "unit_price": 10.00,
                "product_title": "Item",
            }
        ],
        "total_amount": 10.00,
    }
    response = await ac.post("/internal/orders", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_order_internal_empty_items(client):
    ac, _ = client
    payload = {
        "user_id": str(uuid4()),
        "items": [],
        "total_amount": 0.0,
    }
    response = await ac.post("/internal/orders", json=payload)
    # Pydantic does not enforce non-empty list by default — 201 expected
    assert response.status_code == 201
    assert "order_id" in response.json()
