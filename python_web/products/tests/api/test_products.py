import pytest
from decimal import Decimal

from src.app.infra.database.models import CategoryDb, ProductDb


@pytest.mark.asyncio
async def test_get_products_empty(client):
    ac, _ = client
    resp = await ac.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_products_returns_active_products(client, seed_product):
    ac, _ = client
    resp = await ac.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Test Product"


@pytest.mark.asyncio
async def test_get_products_excludes_deleted(
    client, db_session, seed_brand, seed_category, seed_supplier
):
    product = ProductDb(
        category_id=seed_category.id,
        supplier_id=seed_supplier.id,
        brand_id=seed_brand.id,
        title="Deleted Product",
        price=Decimal("10.00"),
        cost_price=Decimal("5.00"),
        sku="DEL-001",
        is_active=True,
        is_deleted=True,
    )
    db_session.add(product)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_products_excludes_inactive(
    client, db_session, seed_brand, seed_category, seed_supplier
):
    product = ProductDb(
        category_id=seed_category.id,
        supplier_id=seed_supplier.id,
        brand_id=seed_brand.id,
        title="Inactive Product",
        price=Decimal("10.00"),
        cost_price=Decimal("5.00"),
        sku="INACT-001",
        is_active=False,
        is_deleted=False,
    )
    db_session.add(product)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_get_products_with_category_filter(
    client, db_session, seed_product, seed_brand, seed_supplier
):
    other_cat = CategoryDb(name="Other", slug="other", is_deleted=False)
    db_session.add(other_cat)
    await db_session.flush()

    other_product = ProductDb(
        category_id=other_cat.id,
        supplier_id=seed_supplier.id,
        brand_id=seed_brand.id,
        title="Other Product",
        price=Decimal("20.00"),
        cost_price=Decimal("10.00"),
        sku="OTH-001",
        is_active=True,
        is_deleted=False,
    )
    db_session.add(other_product)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/", params={"category_id": seed_product.category_id})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Test Product"


@pytest.mark.asyncio
async def test_get_products_with_price_range(
    client, db_session, seed_brand, seed_category, seed_supplier
):
    for i, price in enumerate([10, 50, 100, 200]):
        p = ProductDb(
            category_id=seed_category.id,
            supplier_id=seed_supplier.id,
            brand_id=seed_brand.id,
            title=f"Product {price}",
            price=Decimal(str(price)),
            cost_price=Decimal("5.00"),
            sku=f"PRICE-{i}",
            stock_quantity=10,
            is_active=True,
            is_deleted=False,
        )
        db_session.add(p)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/", params={"min_price": 40, "max_price": 150})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    titles = {item["title"] for item in data["items"]}
    assert titles == {"Product 50", "Product 100"}


@pytest.mark.asyncio
async def test_get_products_pagination(
    client, db_session, seed_brand, seed_category, seed_supplier
):
    for i in range(5):
        p = ProductDb(
            category_id=seed_category.id,
            supplier_id=seed_supplier.id,
            brand_id=seed_brand.id,
            title=f"Paginated Product {i}",
            price=Decimal("10.00"),
            cost_price=Decimal("5.00"),
            sku=f"PAG-{i}",
            stock_quantity=10,
            is_active=True,
            is_deleted=False,
        )
        db_session.add(p)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/", params={"page": 1, "limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["total_pages"] == 3

    resp2 = await ac.get("/", params={"page": 3, "limit": 2})
    data2 = resp2.json()
    assert len(data2["items"]) == 1


@pytest.mark.asyncio
async def test_get_single_product(client, seed_product):
    ac, _ = client
    resp = await ac.get(f"/{seed_product.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["product"]["id"] == seed_product.id
    assert data["product"]["title"] == "Test Product"


@pytest.mark.asyncio
async def test_get_single_product_not_found(client):
    ac, _ = client
    resp = await ac.get("/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_search_products(client, seed_product):
    ac, _ = client
    resp = await ac.get("/search", params={"q": "Test Product"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data["items"], list)
