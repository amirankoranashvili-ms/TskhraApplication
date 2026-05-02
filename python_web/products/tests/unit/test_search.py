import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

from src.app.infra.database.models import ProductDb, BrandDb, ProductImageDb


# ============ ElasticsearchProductRepository ============


@pytest.mark.asyncio
async def test_es_repo_search_products():
    from src.app.infra.search.repository import ElasticsearchProductRepository

    mock_client = AsyncMock()
    mock_client.search.return_value = {
        "hits": {
            "total": {"value": 1},
            "hits": [
                {
                    "_source": {
                        "id": 1,
                        "title": "Phone",
                        "price": 999.0,
                        "cover_image_url": "http://img.png",
                        "brand_id": 1,
                        "brand_name": "Apple",
                        "brand_logo_url": None,
                        "stock_quantity": 5,
                    }
                }
            ],
        }
    }

    repo = ElasticsearchProductRepository(mock_client)
    products, total = await repo.search_products("phone", limit=10, offset=0)

    assert total == 1
    assert products[0].title == "Phone"
    assert products[0].brand.name == "Apple"


@pytest.mark.asyncio
async def test_es_repo_search_with_filters():
    from src.app.infra.search.repository import ElasticsearchProductRepository

    mock_client = AsyncMock()
    mock_client.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}

    repo = ElasticsearchProductRepository(mock_client)
    await repo.search_products(
        "phone",
        limit=10,
        offset=0,
        category_id=5,
        brand_ids=[1, 2],
        min_price=100.0,
        max_price=500.0,
    )

    call_kwargs = mock_client.search.call_args
    body = call_kwargs.kwargs.get("body") or call_kwargs[1].get("body")
    filters = body["query"]["bool"]["filter"]
    assert any(f.get("term", {}).get("category_id") == 5 for f in filters)
    assert any(f.get("terms", {}).get("brand_id") == [1, 2] for f in filters)


@pytest.mark.asyncio
async def test_es_repo_search_with_sort():
    from src.app.infra.search.repository import ElasticsearchProductRepository

    mock_client = AsyncMock()
    mock_client.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}

    repo = ElasticsearchProductRepository(mock_client)
    await repo.search_products("phone", limit=10, offset=0, sort=["price:asc"])

    call_kwargs = mock_client.search.call_args
    body = call_kwargs.kwargs.get("body") or call_kwargs[1].get("body")
    assert body["sort"] == [{"price": {"order": "asc"}}]


@pytest.mark.asyncio
async def test_es_repo_search_with_spec_filters():
    from src.app.infra.search.repository import ElasticsearchProductRepository

    mock_client = AsyncMock()
    mock_client.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}

    repo = ElasticsearchProductRepository(mock_client)
    await repo.search_products(
        "phone",
        limit=10,
        offset=0,
        spec_filters={"Color": ["Red", "Blue"]},
    )

    call_kwargs = mock_client.search.call_args
    body = call_kwargs.kwargs.get("body") or call_kwargs[1].get("body")
    filters = body["query"]["bool"]["filter"]
    assert any(
        f.get("terms", {}).get("spec_fields.Color") == ["Red", "Blue"] for f in filters
    )


@pytest.mark.asyncio
async def test_es_repo_index_product():
    from src.app.infra.search.repository import ElasticsearchProductRepository

    mock_client = AsyncMock()
    repo = ElasticsearchProductRepository(mock_client)
    await repo.index_product({"id": 1, "title": "Test"})
    mock_client.index.assert_awaited_once()


@pytest.mark.asyncio
async def test_es_repo_index_products_batch():
    from src.app.infra.search.repository import ElasticsearchProductRepository

    mock_client = AsyncMock()
    repo = ElasticsearchProductRepository(mock_client)
    await repo.index_products_batch([{"id": 1}, {"id": 2}])
    mock_client.bulk.assert_awaited_once()


@pytest.mark.asyncio
async def test_es_repo_index_products_batch_empty():
    from src.app.infra.search.repository import ElasticsearchProductRepository

    mock_client = AsyncMock()
    repo = ElasticsearchProductRepository(mock_client)
    await repo.index_products_batch([])
    mock_client.bulk.assert_not_awaited()


@pytest.mark.asyncio
async def test_es_repo_delete_product_document():
    from src.app.infra.search.repository import ElasticsearchProductRepository

    mock_client = AsyncMock()
    repo = ElasticsearchProductRepository(mock_client)
    await repo.delete_product_document(42)
    mock_client.delete.assert_awaited_once_with(index="products", id="42")


# ============ product_orm_to_search_document ============


def test_product_orm_to_search_document():
    from src.app.infra.search.sync import product_orm_to_search_document

    brand = MagicMock(spec=BrandDb)
    brand.name = "TestBrand"
    brand.logo_url = "http://logo.png"

    img = MagicMock(spec=ProductImageDb)
    img.image_url = "http://img1.png"

    category = MagicMock()
    category.name = "Phones"

    product = MagicMock(spec=ProductDb)
    product.id = 1
    product.title = "Test"
    product.description = "Desc"
    product.price = Decimal("99.99")
    product.sku = "SKU-1"
    product.category_id = 1
    product.brand_id = 1
    product.brand = brand
    product.category = category
    product.cover_image_url = "http://cover.png"
    product.stock_quantity = 10
    product.is_active = True
    product.is_deleted = False
    product.images = [img]
    product.field_values = []
    product.created_at = None
    product.updated_at = None

    doc = product_orm_to_search_document(product)
    assert doc["id"] == 1
    assert doc["title"] == "Test"
    assert doc["brand_name"] == "TestBrand"
    assert doc["cover_image_url"] == "http://cover.png"
    assert doc["category_name"] == "Phones"
    assert doc["spec_values"] == []
    assert doc["spec_fields"] == {}


def test_product_orm_to_search_document_no_cover():
    from src.app.infra.search.sync import product_orm_to_search_document

    product = MagicMock(spec=ProductDb)
    product.id = 2
    product.title = "NoCover"
    product.description = None
    product.price = Decimal("10.00")
    product.sku = "SKU-2"
    product.category_id = 1
    product.brand_id = 1
    product.brand = None
    product.category = None
    product.cover_image_url = None
    product.stock_quantity = 0
    product.is_active = True
    product.is_deleted = False
    product.images = []
    product.field_values = []
    product.created_at = None
    product.updated_at = None

    doc = product_orm_to_search_document(product)
    assert doc["cover_image_url"] is None
    assert doc["brand_name"] == ""
    assert doc["description"] == ""
    assert doc["category_name"] == ""


def test_product_orm_to_search_document_with_specs():
    from src.app.infra.search.sync import product_orm_to_search_document

    brand = MagicMock(spec=BrandDb)
    brand.name = "TestBrand"
    brand.logo_url = None

    category = MagicMock()
    category.name = "Electronics"

    field_color = MagicMock()
    field_color.name = "Color"
    option_red = MagicMock()
    option_red.value = "Red"
    fv1 = MagicMock()
    fv1.option = option_red
    fv1.field = field_color
    fv1.field_id = 1

    field_storage = MagicMock()
    field_storage.name = "Storage"
    option_128 = MagicMock()
    option_128.value = "128GB"
    fv2 = MagicMock()
    fv2.option = option_128
    fv2.field = field_storage
    fv2.field_id = 2

    product = MagicMock(spec=ProductDb)
    product.id = 3
    product.title = "Phone"
    product.description = "A phone"
    product.price = Decimal("599.99")
    product.sku = "SKU-3"
    product.category_id = 1
    product.brand_id = 1
    product.brand = brand
    product.category = category
    product.cover_image_url = None
    product.stock_quantity = 5
    product.is_active = True
    product.is_deleted = False
    product.images = []
    product.field_values = [fv1, fv2]
    product.created_at = None
    product.updated_at = None

    doc = product_orm_to_search_document(product)
    assert "Red" in doc["spec_values"]
    assert "128GB" in doc["spec_values"]
    assert doc["spec_fields"]["Color"] == ["Red"]
    assert doc["spec_fields"]["Storage"] == ["128GB"]


# ============ sync_all_products ============


@pytest.mark.asyncio
async def test_sync_all_products(db_session, seed_product):
    from src.app.infra.search.sync import sync_all_products

    mock_search = AsyncMock()
    await sync_all_products(db_session, mock_search)

    mock_search.index_products_batch.assert_awaited()


@pytest.mark.asyncio
async def test_sync_all_products_empty(db_session):
    from src.app.infra.search.sync import sync_all_products

    mock_search = AsyncMock()
    await sync_all_products(db_session, mock_search)

    mock_search.index_products_batch.assert_not_awaited()


# ============ client ============


@pytest.mark.asyncio
async def test_get_elasticsearch_client():
    from src.app.infra.search.client import get_elasticsearch_client

    client = get_elasticsearch_client()
    assert client is not None
    await client.close()


@pytest.mark.asyncio
async def test_setup_elasticsearch_index():
    from src.app.infra.search.client import setup_elasticsearch_index

    mock_client = AsyncMock()
    mock_client.indices = AsyncMock()
    mock_client.indices.exists.return_value = False
    mock_client.indices.create = AsyncMock()
    mock_client.close = AsyncMock()

    with patch("src.app.infra.search.client.get_elasticsearch_client", return_value=mock_client):
        await setup_elasticsearch_index()

    mock_client.indices.create.assert_awaited_once()
    mock_client.close.assert_awaited_once()
