import pytest
from unittest.mock import AsyncMock

from src.app.core.products.service import ProductService, BrandService
from src.app.core.products.exceptions import (
    ProductNotFoundException,
    BrandNotFoundException,
)
from src.app.core.products.entities import (
    ProductDomainModel,
    Brand,
    ProductImageDomainModel,
    SortByOption,
)
from src.app.core.schemas.product_schemas import ProductSlim
from src.app.core.interactors.handle_product_upload import HandleProductUploadInteractor
from src.app.core.interactors.handle_product_update import HandleProductUpdateInteractor


def _make_domain_product(**overrides):
    defaults = dict(
        id=1,
        category_id=1,
        supplier_id=1,
        title="Test Product",
        description="desc",
        price=99.99,
        sku="SKU-001",
        stock_quantity=10,
        cover_image_url="http://img.png",
        brand=Brand(id=1, name="Brand", logo_url=None),
        images=[ProductImageDomainModel(id=1, image_url="http://img.png")],
        field_values=[],
        category=None,
    )
    defaults.update(overrides)
    return ProductDomainModel(**defaults)


def _make_slim(**overrides):
    defaults = dict(
        id=1,
        brand=Brand(id=1, name="Brand", logo_url=None),
        price=99.99,
        title="Test Product",
        cover_image_url="http://img.png",
        stock_quantity=10,
        sku="SKU-001",
        images=["http://img.png"],
    )
    defaults.update(overrides)
    return ProductSlim(**defaults)


@pytest.mark.asyncio
async def test_get_product_success():
    repo = AsyncMock()
    repo.get_by_id.return_value = _make_domain_product()

    service = ProductService(repo)
    result = await service.get_product(1)

    assert result.id == 1
    assert result.title == "Test Product"
    repo.get_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_product_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None

    service = ProductService(repo)
    with pytest.raises(ProductNotFoundException):
        await service.get_product(1)


@pytest.mark.asyncio
async def test_search_products():
    repo = AsyncMock()
    repo.search_products.return_value = ([_make_slim()], 1)

    service = ProductService(repo)
    items, total = await service.search_products("test", limit=20, offset=0)

    assert total == 1
    assert len(items) == 1
    repo.search_products.assert_awaited_once_with("test", 20, 0)


@pytest.mark.asyncio
async def test_get_products_delegates_to_repo():
    repo = AsyncMock()
    repo.get_products.return_value = ([_make_slim()], 1)

    service = ProductService(repo)
    items, total = await service.get_products(
        category_id=1,
        supplier_id=None,
        limit=20,
        offset=0,
        min_price=None,
        max_price=None,
        sort_by=SortByOption.POPULAR,
        dynamic_filters={},
    )

    assert total == 1
    assert len(items) == 1


# --- Interactor tests ---


@pytest.mark.asyncio
async def test_handle_product_upload_success():
    repo = AsyncMock()
    repo.create_product.return_value = _make_domain_product(id=42)

    interactor = HandleProductUploadInteractor(repo)
    payload = {
        "task_id": "abc",
        "supplier_id": 1,
        "is_provider": True,
        "category_id": 1,
        "brand_id": 1,
        "title": "New Product",
        "price": 99.99,
        "sku": "NEW-001",
    }
    result = await interactor.execute(payload)
    assert result["status"] == "SUCCESS"
    assert result["product_id"] == 42


@pytest.mark.asyncio
async def test_handle_product_upload_failure():
    repo = AsyncMock()
    repo.create_product.side_effect = Exception("DB error")

    interactor = HandleProductUploadInteractor(repo)
    payload = {
        "task_id": "abc",
        "supplier_id": 1,
        "is_provider": True,
        "category_id": 1,
        "brand_id": 1,
        "title": "New Product",
        "price": 99.99,
        "sku": "NEW-001",
    }
    result = await interactor.execute(payload)
    assert result["status"] == "FAILED"
    assert result["error_message"] == "DB error"


@pytest.mark.asyncio
async def test_handle_product_update_success():
    repo = AsyncMock()
    repo.update_product.return_value = None

    interactor = HandleProductUpdateInteractor(repo)
    payload = {
        "task_id": "upd",
        "product_id": 1,
        "supplier_id": 1,
        "title": "Updated",
    }
    result = await interactor.execute(payload)
    assert result["status"] == "SUCCESS"
    assert result["product_id"] == 1


@pytest.mark.asyncio
async def test_handle_product_update_resubmission():
    repo = AsyncMock()
    repo.reactivate_rejected_product.return_value = None

    interactor = HandleProductUpdateInteractor(repo)
    payload = {
        "task_id": "resub",
        "product_id": 5,
        "supplier_id": 1,
        "is_resubmission": True,
        "title": "Resubmitted",
    }
    result = await interactor.execute(payload)
    assert result["status"] == "SUCCESS"
    repo.reactivate_rejected_product.assert_awaited_once()
    repo.update_product.assert_not_awaited()


# --- Brand service tests ---


@pytest.mark.asyncio
async def test_brand_service_get_by_id_success():
    repo = AsyncMock()
    repo.get_by_id.return_value = Brand(id=1, name="TestBrand", logo_url=None)

    service = BrandService(repo)
    result = await service.get_brand_by_id(1)
    assert result.name == "TestBrand"


@pytest.mark.asyncio
async def test_brand_service_get_by_id_not_found():
    repo = AsyncMock()
    repo.get_by_id.return_value = None

    service = BrandService(repo)
    with pytest.raises(BrandNotFoundException):
        await service.get_brand_by_id(1)
