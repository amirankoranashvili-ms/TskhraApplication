import pytest
from decimal import Decimal

from src.app.infra.database.models import ProductDb


@pytest.mark.asyncio
async def test_get_product_availability(client, seed_product):
    ac, _ = client
    resp = await ac.get(f"/internal/products/availability/{seed_product.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == seed_product.id
    assert data["title"] == "Test Product"
    assert data["price"] == 99.99
    assert data["stock_quantity"] == 10


@pytest.mark.asyncio
async def test_get_product_availability_not_found(client):
    ac, _ = client
    resp = await ac.get("/internal/products/availability/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_products_availability_batch(
    client, db_session, seed_product, seed_brand, seed_category, seed_supplier
):
    product2 = ProductDb(
        category_id=seed_category.id,
        supplier_id=seed_supplier.id,
        brand_id=seed_brand.id,
        title="Second Product",
        price=Decimal("49.99"),
        cost_price=Decimal("20.00"),
        sku="BATCH-002",
        stock_quantity=5,
        is_active=True,
        is_deleted=False,
    )
    db_session.add(product2)
    await db_session.commit()
    await db_session.refresh(product2)

    ac, _ = client
    resp = await ac.post(
        "/internal/products/availability/batch",
        json=[seed_product.id, product2.id],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    ids = {item["id"] for item in data}
    assert ids == {seed_product.id, product2.id}


@pytest.mark.asyncio
async def test_get_products_availability_batch_empty(client):
    ac, _ = client
    resp = await ac.post("/internal/products/availability/batch", json=[])
    assert resp.status_code == 200
    assert resp.json() == []
