import pytest
from decimal import Decimal

from src.app.infra.database.models import (
    FieldDb,
    FieldGroupDb,
    FieldOptionDb,
    ProductDb,
    ProductFieldValueDb,
    ProductImageDb,
)


@pytest.mark.asyncio
async def test_get_products_with_dynamic_filters(
    client, db_session, seed_brand, seed_category, seed_supplier
):
    product = ProductDb(
        category_id=seed_category.id,
        supplier_id=seed_supplier.id,
        brand_id=seed_brand.id,
        title="Dynamic Filter Product",
        price=Decimal("50.00"),
        cost_price=Decimal("25.00"),
        sku="DYN-001",
        is_active=True,
        is_deleted=False,
    )
    db_session.add(product)
    await db_session.flush()

    group = FieldGroupDb(name="DynGroup")
    db_session.add(group)
    await db_session.flush()

    field = FieldDb(name="DynField", group_id=group.id)
    db_session.add(field)
    await db_session.flush()

    option = FieldOptionDb(field_id=field.id, value="DynValue")
    db_session.add(option)
    await db_session.flush()

    fv = ProductFieldValueDb(
        product_id=product.id, field_id=field.id, option_id=option.id
    )
    db_session.add(fv)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/", params={"dynfield": str(option.id)})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_products_with_supplier_filter(client, seed_product):
    ac, _ = client
    resp = await ac.get("/", params={"supplier_id": seed_product.supplier_id})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_products_sort_newest(client, seed_product):
    ac, _ = client
    resp = await ac.get("/", params={"sort_by": "newest"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_products_sort_price_asc(client, seed_product):
    ac, _ = client
    resp = await ac.get("/", params={"sort_by": "price_asc"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_products_sort_price_desc(client, seed_product):
    ac, _ = client
    resp = await ac.get("/", params={"sort_by": "price_desc"})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_search_products_pagination(
    client, db_session, seed_brand, seed_category, seed_supplier
):
    for i in range(3):
        p = ProductDb(
            category_id=seed_category.id,
            supplier_id=seed_supplier.id,
            brand_id=seed_brand.id,
            title=f"Searchable Item {i}",
            price=Decimal("10.00"),
            cost_price=Decimal("5.00"),
            sku=f"SRCH-{i}",
            is_active=True,
            is_deleted=False,
        )
        db_session.add(p)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/search", params={"q": "Searchable", "page": 1, "limit": 2})
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_product_with_full_details(
    client, db_session, seed_brand, seed_category, seed_supplier
):
    product = ProductDb(
        category_id=seed_category.id,
        supplier_id=seed_supplier.id,
        brand_id=seed_brand.id,
        title="Detailed Product",
        description="Full description here",
        price=Decimal("199.99"),
        cost_price=Decimal("100.00"),
        sku="DET-001",
        stock_quantity=25,
        cover_image_url=None,
        is_active=True,
        is_deleted=False,
    )
    db_session.add(product)
    await db_session.flush()

    img1 = ProductImageDb(product_id=product.id, image_url="http://img1.png")
    img2 = ProductImageDb(product_id=product.id, image_url="http://img2.png")
    db_session.add_all([img1, img2])
    await db_session.commit()

    ac, _ = client
    resp = await ac.get(f"/{product.id}")
    assert resp.status_code == 200
    data = resp.json()["product"]
    assert data["title"] == "Detailed Product"
    assert data["image_url"] == "http://img1.png"
    assert len(data["images"]) == 2
