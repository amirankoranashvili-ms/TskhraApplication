import pytest
from unittest.mock import AsyncMock

from src.app.core.categories.service import CategoryService
from src.app.core.categories.exceptions import CategoryNotFoundException
from src.app.core.categories.entities import (
    Category,
    CategoryFieldDomainModel,
    FieldDomainModel,
    FieldOptionDomainModel,
    FieldGroupDomainModel,
    CategoryWithProductsDomainModel,
)
from src.app.core.products.entities import (
    Brand,
    ProductDomainModel,
    ProductImageDomainModel,
)


def _make_category(**overrides):
    defaults = dict(
        id=1,
        parent_id=None,
        name="Cat",
        slug="cat",
        image_url=None,
        has_subcategories=False,
        product_count=0,
        brands=[],
    )
    defaults.update(overrides)
    return Category(**defaults)


@pytest.mark.asyncio
async def test_get_categories():
    cat_repo = AsyncMock()
    cat_repo.get_all.return_value = [_make_category()]
    field_repo = AsyncMock()

    service = CategoryService(cat_repo, field_repo)
    result = await service.get_categories(None)
    assert len(result.categories) == 1
    assert result.categories[0].name == "Cat"


@pytest.mark.asyncio
async def test_get_categories_with_products():
    product = ProductDomainModel(
        id=1,
        category_id=1,
        supplier_id=1,
        title="Prod",
        price=10.0,
        sku="S1",
        stock_quantity=5,
        brand=Brand(id=1, name="B", logo_url=None),
        images=[ProductImageDomainModel(id=1, image_url="http://img.png")],
        field_values=[],
        category=None,
    )
    cat_with_prods = CategoryWithProductsDomainModel(
        id=1,
        parent_id=None,
        name="Cat",
        slug="cat",
        has_subcategories=False,
        products=[product],
    )
    cat_repo = AsyncMock()
    cat_repo.get_categories_with_top_products.return_value = [cat_with_prods]
    field_repo = AsyncMock()

    service = CategoryService(cat_repo, field_repo)
    result = await service.get_categories_with_products(None)
    assert len(result.categories) == 1
    assert len(result.categories[0].products) == 1
    assert result.categories[0].products[0].title == "Prod"


@pytest.mark.asyncio
async def test_get_filters_success():
    cat_repo = AsyncMock()
    cat_repo.get_by_id.return_value = _make_category()

    group = FieldGroupDomainModel(id=2, name="Specs")
    field = FieldDomainModel(id=10, name="Color", group_id=2, group=group)
    option = FieldOptionDomainModel(id=100, field_id=10, value="Red")
    cf = CategoryFieldDomainModel(
        id=1,
        category_id=1,
        field_id=10,
        is_required=False,
        field=field,
        option=option,
    )
    field_repo = AsyncMock()
    field_repo.get_fields_and_options_for_category.return_value = [cf]
    field_repo.get_option_product_counts.return_value = {100: 5}
    field_repo.get_brand_product_counts.return_value = {}

    service = CategoryService(cat_repo, field_repo)
    result = await service.get_filters(1)
    assert len(result.filters) >= 1
    found = False
    for f in result.filters:
        for fld in f.fields:
            if fld.field_name == "Color":
                found = True
                assert fld.options[0].option_value == "Red"
                assert fld.options[0].product_count == 5
    assert found


@pytest.mark.asyncio
async def test_get_filters_with_brands():
    brand = Brand(id=5, name="Nike", logo_url=None)
    cat_repo = AsyncMock()
    cat_repo.get_by_id.return_value = _make_category(brands=[brand])
    field_repo = AsyncMock()
    field_repo.get_fields_and_options_for_category.return_value = []
    field_repo.get_option_product_counts.return_value = {}
    field_repo.get_brand_product_counts.return_value = {5: 3}

    service = CategoryService(cat_repo, field_repo)
    result = await service.get_filters(1)
    assert len(result.brands) >= 1
    assert result.brands[0].brand_name == "Nike"
    assert result.brands[0].product_count == 3


@pytest.mark.asyncio
async def test_get_filters_category_not_found():
    cat_repo = AsyncMock()
    cat_repo.get_by_id.return_value = None
    field_repo = AsyncMock()

    service = CategoryService(cat_repo, field_repo)
    with pytest.raises(CategoryNotFoundException):
        await service.get_filters(999)
