import pytest

from src.app.infra.database.models import (
    CategoryDb,
    CategoryFieldDb,
    FieldDb,
    FieldGroupDb,
    FieldOptionDb,
)


@pytest.mark.asyncio
async def test_get_categories_empty(client):
    ac, _ = client
    resp = await ac.get("/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert data["categories"] == []


@pytest.mark.asyncio
async def test_get_categories_root(client, seed_category):
    ac, _ = client
    resp = await ac.get("/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["categories"]) == 1
    assert data["categories"][0]["name"] == "TestCategory"
    assert data["categories"][0]["parent_id"] is None


@pytest.mark.asyncio
async def test_get_categories_with_parent_id(client, db_session, seed_category):
    sub = CategoryDb(
        name="SubCategory",
        slug="sub-category",
        parent_id=seed_category.id,
        is_deleted=False,
    )
    db_session.add(sub)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/categories", params={"parent_id": seed_category.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["categories"]) == 1
    assert data["categories"][0]["name"] == "SubCategory"


@pytest.mark.asyncio
async def test_get_categories_excludes_deleted(client, db_session):
    deleted_cat = CategoryDb(
        name="Deleted",
        slug="deleted",
        is_deleted=True,
    )
    db_session.add(deleted_cat)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/categories")
    assert resp.status_code == 200
    assert resp.json()["categories"] == []


@pytest.mark.asyncio
async def test_get_categories_with_products(client, seed_product):
    ac, _ = client
    resp = await ac.get("/categories/products")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["categories"]) >= 1


@pytest.mark.asyncio
async def test_get_filters(client, db_session, seed_category):
    group = FieldGroupDb(name="TestGroup")
    db_session.add(group)
    await db_session.flush()

    field = FieldDb(name="Color", group_id=group.id)
    db_session.add(field)
    await db_session.flush()

    option = FieldOptionDb(field_id=field.id, value="Red")
    db_session.add(option)

    cf = CategoryFieldDb(
        category_id=seed_category.id,
        field_id=field.id,
        is_required=False,
    )
    db_session.add(cf)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/filters", params={"category_id": seed_category.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["filters"]) >= 1
    assert data["filters"][0]["fields"][0]["field_name"] == "Color"


@pytest.mark.asyncio
async def test_get_filters_category_not_found(client):
    ac, _ = client
    resp = await ac.get("/filters", params={"category_id": 99999})
    assert resp.status_code == 404
