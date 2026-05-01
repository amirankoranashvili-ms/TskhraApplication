import pytest
import pytest_asyncio
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from src.app.infra.database.models import (
    BrandDb,
    CategoryDb,
    SupplierDb,
    ProductDb,
    ProductImageDb,
    FieldGroupDb,
    FieldDb,
    FieldOptionDb,
    CategoryFieldDb,
    VerificationRequestDb,
)
from src.app.infra.database.repositories import (
    SqlAlchemyCategoryRepository,
    SqlAlchemyCategoryFieldRepository,
    SqlAlchemyProductRepository,
    SqlAlchemyBrandRepository,
    SqlAlchemySellerRepository,
    SqlAlchemyVerificationRequestRepository,
)
from src.app.core.schemas.product_schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
)


@pytest_asyncio.fixture
async def base_data(db_session):
    brand = BrandDb(name="RepoBrand", logo_url="http://logo.png", is_deleted=False)
    db_session.add(brand)
    await db_session.flush()

    category = CategoryDb(name="RepoCat", slug="repo-cat", is_deleted=False)
    db_session.add(category)
    await db_session.flush()

    supplier = SupplierDb(
        name="RepoSupplier", supplier_type="external", is_deleted=False
    )
    db_session.add(supplier)
    await db_session.flush()

    await db_session.commit()
    return brand, category, supplier


@pytest_asyncio.fixture
async def product_in_db(db_session, base_data):
    brand, category, supplier = base_data
    product = ProductDb(
        category_id=category.id,
        supplier_id=supplier.id,
        brand_id=brand.id,
        title="Repo Product",
        description="Description",
        price=Decimal("99.99"),
        cost_price=Decimal("50.00"),
        sku="REPO-SKU-001",
        stock_quantity=10,
        cover_image_url="http://cover.png",
        is_active=True,
        is_deleted=False,
    )
    db_session.add(product)
    await db_session.flush()

    img = ProductImageDb(product_id=product.id, image_url="http://img1.png")
    db_session.add(img)

    await db_session.commit()
    await db_session.refresh(product)
    return product


# ============ CategoryRepository ============


@pytest.mark.asyncio
async def test_category_repo_get_all(db_session, base_data):
    _, category, _ = base_data
    repo = SqlAlchemyCategoryRepository(db_session)
    categories = await repo.get_all()
    assert len(categories) >= 1
    assert any(c.name == "RepoCat" for c in categories)


@pytest.mark.asyncio
async def test_category_repo_get_all_with_parent(db_session, base_data):
    _, parent, _ = base_data
    sub = CategoryDb(
        name="SubCat", slug="sub-cat", parent_id=parent.id, is_deleted=False
    )
    db_session.add(sub)
    await db_session.commit()

    repo = SqlAlchemyCategoryRepository(db_session)
    children = await repo.get_all(parent_id=parent.id)
    assert len(children) == 1
    assert children[0].name == "SubCat"


@pytest.mark.asyncio
async def test_category_repo_get_by_id(db_session, base_data):
    _, category, _ = base_data
    repo = SqlAlchemyCategoryRepository(db_session)
    result = await repo.get_by_id(category.id)
    assert result is not None
    assert result.name == "RepoCat"


@pytest.mark.asyncio
async def test_category_repo_get_by_id_not_found(db_session):
    repo = SqlAlchemyCategoryRepository(db_session)
    result = await repo.get_by_id(99999)
    assert result is None


@pytest.mark.asyncio
async def test_category_repo_get_categories_with_top_products(
    db_session, product_in_db, base_data
):
    repo = SqlAlchemyCategoryRepository(db_session)
    result = await repo.get_categories_with_top_products(limit_per_cat=4)
    assert len(result) >= 1


# ============ CategoryFieldRepository ============


@pytest.mark.asyncio
async def test_category_field_repo_get_fields(db_session, base_data):
    _, category, _ = base_data

    group = FieldGroupDb(name="General")
    db_session.add(group)
    await db_session.flush()

    field = FieldDb(name="TestField", group_id=group.id)
    db_session.add(field)
    await db_session.flush()

    option = FieldOptionDb(field_id=field.id, value="Value1")
    db_session.add(option)

    cf = CategoryFieldDb(category_id=category.id, field_id=field.id, is_required=True)
    db_session.add(cf)
    await db_session.commit()

    repo = SqlAlchemyCategoryFieldRepository(db_session)
    fields = await repo.get_fields_and_options_for_category(category.id)
    assert len(fields) >= 1
    assert fields[0].field.name == "TestField"


# ============ ProductRepository ============


@pytest.mark.asyncio
async def test_product_repo_get_by_id(db_session, product_in_db):
    repo = SqlAlchemyProductRepository(db_session)
    result = await repo.get_by_id(product_in_db.id)
    assert result is not None
    assert result.title == "Repo Product"


@pytest.mark.asyncio
async def test_product_repo_get_by_id_not_found(db_session):
    repo = SqlAlchemyProductRepository(db_session)
    result = await repo.get_by_id(99999)
    assert result is None


@pytest.mark.asyncio
async def test_product_repo_search_products(db_session, product_in_db):
    repo = SqlAlchemyProductRepository(db_session)
    results, total = await repo.search_products("Repo", limit=10, offset=0)
    assert total >= 1
    assert any(p.title == "Repo Product" for p in results)


@pytest.mark.asyncio
async def test_product_repo_get_products(db_session, product_in_db):
    repo = SqlAlchemyProductRepository(db_session)
    from src.app.core.products.entities import SortByOption

    results, total = await repo.get_products(
        category_id=None,
        supplier_id=None,
        limit=10,
        offset=0,
        min_price=None,
        max_price=None,
        sort_by=SortByOption.POPULAR,
        dynamic_filters={},
    )
    assert total >= 1


@pytest.mark.asyncio
async def test_product_repo_get_products_with_filters(
    db_session, product_in_db, base_data
):
    brand, category, _ = base_data
    repo = SqlAlchemyProductRepository(db_session)
    from src.app.core.products.entities import SortByOption

    results, total = await repo.get_products(
        category_id=category.id,
        supplier_id=None,
        limit=10,
        offset=0,
        min_price=50.0,
        max_price=150.0,
        sort_by=SortByOption.PRICE_ASC,
        dynamic_filters={"brand_id": [brand.id]},
    )
    assert total >= 1


@pytest.mark.asyncio
async def test_product_repo_get_products_price_desc_sort(db_session, product_in_db):
    repo = SqlAlchemyProductRepository(db_session)
    from src.app.core.products.entities import SortByOption

    results, _ = await repo.get_products(
        category_id=None,
        supplier_id=None,
        limit=10,
        offset=0,
        min_price=None,
        max_price=None,
        sort_by=SortByOption.PRICE_DESC,
        dynamic_filters={},
    )
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_product_repo_get_products_newest_sort(db_session, product_in_db):
    repo = SqlAlchemyProductRepository(db_session)
    from src.app.core.products.entities import SortByOption

    results, _ = await repo.get_products(
        category_id=None,
        supplier_id=None,
        limit=10,
        offset=0,
        min_price=None,
        max_price=None,
        sort_by=SortByOption.NEWEST,
        dynamic_filters={},
    )
    assert len(results) >= 1


@pytest.mark.asyncio
async def test_product_repo_create_product(db_session, base_data):
    brand, category, supplier = base_data
    repo = SqlAlchemyProductRepository(db_session)

    req = ProductCreateRequest(
        category_id=category.id,
        supplier_id=supplier.id,
        brand_id=brand.id,
        title="Created Product",
        price=29.99,
        sku="CREATE-001",
        images=["http://new-img.png"],
    )
    result = await repo.create_product(req, is_provider=True)
    assert result is not None
    assert result.title == "Created Product"


@pytest.mark.asyncio
async def test_product_repo_update_product(db_session, product_in_db):
    repo = SqlAlchemyProductRepository(db_session)

    update_req = ProductUpdateRequest(
        title="Updated Title",
        price=149.99,
        images=["http://new-img.png"],
        deleted_images=["http://img1.png"],
    )
    await repo.update_product(product_in_db.id, update_req)

    await db_session.refresh(product_in_db)
    assert product_in_db.title == "Updated Title"
    assert float(product_in_db.price) == 149.99
    assert product_in_db.is_active is False


@pytest.mark.asyncio
async def test_product_repo_update_product_not_found(db_session):
    repo = SqlAlchemyProductRepository(db_session)
    with pytest.raises(ValueError, match="not found"):
        await repo.update_product(99999, ProductUpdateRequest(title="X"))


@pytest.mark.asyncio
async def test_product_repo_delete_product(db_session, product_in_db, base_data):
    _, _, supplier = base_data
    repo = SqlAlchemyProductRepository(db_session)
    await repo.delete_product(product_in_db.id, supplier.id)

    await db_session.refresh(product_in_db)
    assert product_in_db.is_deleted is True
    assert product_in_db.is_active is False


@pytest.mark.asyncio
async def test_product_repo_delete_product_not_found(db_session):
    repo = SqlAlchemyProductRepository(db_session)
    with pytest.raises(ValueError, match="not found"):
        await repo.delete_product(99999, 1)


@pytest.mark.asyncio
async def test_product_repo_reactivate_rejected(db_session, base_data):
    brand, category, supplier = base_data
    product = ProductDb(
        category_id=category.id,
        supplier_id=supplier.id,
        brand_id=brand.id,
        title="Rejected",
        price=Decimal("10.00"),
        cost_price=Decimal("5.00"),
        sku="REJECT-001",
        is_active=False,
        is_deleted=True,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    repo = SqlAlchemyProductRepository(db_session)
    update_req = ProductUpdateRequest(title="Resubmitted")
    await repo.reactivate_rejected_product(product.id, update_req)

    await db_session.refresh(product)
    assert product.title == "Resubmitted"
    assert product.is_deleted is False
    assert product.is_active is False


@pytest.mark.asyncio
async def test_product_repo_reactivate_not_found(db_session):
    repo = SqlAlchemyProductRepository(db_session)
    with pytest.raises(ValueError, match="not found"):
        await repo.reactivate_rejected_product(99999, ProductUpdateRequest(title="X"))


# ============ BrandRepository ============


@pytest.mark.asyncio
async def test_brand_repo_get_by_id(db_session, base_data):
    brand, _, _ = base_data
    repo = SqlAlchemyBrandRepository(db_session)
    result = await repo.get_by_id(brand.id)
    assert result is not None
    assert result.name == "RepoBrand"


@pytest.mark.asyncio
async def test_brand_repo_get_by_id_not_found(db_session):
    repo = SqlAlchemyBrandRepository(db_session)
    result = await repo.get_by_id(99999)
    assert result is None


# ============ SellerRepository ============


@pytest.mark.asyncio
async def test_seller_repo_create(db_session):
    repo = SqlAlchemySellerRepository(db_session)
    user_id = str(uuid4())
    await repo.create_seller(
        {
            "supplier_id": 100,
            "name": "Test Seller",
            "user_id": user_id,
            "identification_number": "ID123",
            "legal_address": "Test Address",
            "contact_phone": "+123",
            "contact_email": "test@example.com",
            "bank_account_number": "ACC123",
        }
    )

    stmt = select(SupplierDb).where(SupplierDb.id == 100)
    result = await db_session.execute(stmt)
    supplier = result.scalar_one_or_none()
    assert supplier is not None
    assert supplier.name == "Test Seller"


@pytest.mark.asyncio
async def test_seller_repo_update(db_session):
    repo = SqlAlchemySellerRepository(db_session)
    user_id = str(uuid4())

    await repo.create_seller(
        {
            "supplier_id": 200,
            "name": "Original",
            "user_id": user_id,
            "identification_number": "ID456",
            "legal_address": "Address",
        }
    )

    await repo.update_seller(
        {
            "supplier_id": 200,
            "name": "Updated Seller",
            "identification_number": "ID789",
            "legal_address": "New Address",
            "contact_phone": "+999",
        }
    )

    stmt = select(SupplierDb).where(SupplierDb.id == 200)
    result = await db_session.execute(stmt)
    supplier = result.scalar_one()
    assert supplier.name == "Updated Seller"


# ============ VerificationRequestRepository ============


@pytest.mark.asyncio
async def test_verification_request_repo_create(db_session, base_data):
    _, _, supplier = base_data
    repo = SqlAlchemyVerificationRequestRepository(db_session)
    await repo.create_verification_request(
        request_type="seller",
        supplier_id=supplier.id,
    )

    stmt = select(VerificationRequestDb).where(
        VerificationRequestDb.supplier_id == supplier.id
    )
    result = await db_session.execute(stmt)
    vr = result.scalar_one_or_none()
    assert vr is not None
    assert vr.request_type == "seller"
