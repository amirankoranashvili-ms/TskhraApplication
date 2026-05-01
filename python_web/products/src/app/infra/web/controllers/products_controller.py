"""Products API controller.

Defines the FastAPI routes for the products service, including public
endpoints for browsing, searching, and filtering products, as well as
internal endpoints for inter-service communication.
"""

from fastapi import APIRouter, Query, Request, Depends, HTTPException, Body
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from typing import Optional, List, Dict, Any

from starlette import status

from src.app.core.schemas.category_schemas import (
    GetAllCategoriesResponse,
    GetCategoryFiltersResponse,
    GetCategoriesWithProductsResponse,
)
from src.app.core.schemas.product_schemas import (
    GetProductResponse,
    ProductSearchResponse,
)
from src.app.core.config import settings
from src.app.infra.database.config import engine, get_db
from src.app.infra.web.dependables import (
    CategoryServiceDep,
    GetProductDep,
    ListProductsDep,
    SearchProductsDep,
    GetFiltersDep,
    SearchRepoDep,
)

products_api = APIRouter()

STATIC_PARAMS = {
    "category_id",
    "supplier_id",
    "page",
    "limit",
    "min_price",
    "max_price",
    "sort_by",
    "in_stock",
}

SEARCH_STATIC_PARAMS = {
    "q",
    "page",
    "limit",
    "in_stock",
    "category_id",
    "min_price",
    "max_price",
    "sort_by",
}


@products_api.get("/health", include_in_schema=False)
async def health():
    """Check database connectivity and return service health status."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok"}


@products_api.get(
    "/categories",
    status_code=status.HTTP_200_OK,
    response_model=GetAllCategoriesResponse,
)
async def get_all_categories(
    service: CategoryServiceDep,
    parent_id: Optional[int] = Query(None),
):
    """Retrieve all categories, optionally filtered by parent ID.

    Args:
        service: Injected category service dependency.
        parent_id: Optional parent category ID filter.

    Returns:
        A response containing the list of categories.
    """
    return await service.get_categories(parent_id)


@products_api.get(
    "/categories/products",
    status_code=status.HTTP_200_OK,
    response_model=GetCategoriesWithProductsResponse,
)
async def get_categories_with_products(
    service: CategoryServiceDep,
    parent_id: Optional[int] = Query(None),
):
    """Retrieve categories with their top products embedded.

    Args:
        service: Injected category service dependency.
        parent_id: Optional parent category ID filter.

    Returns:
        A response containing categories with product lists.
    """
    return await service.get_categories_with_products(parent_id)


@products_api.get(
    "/", status_code=status.HTTP_200_OK, response_model=ProductSearchResponse
)
async def get_products(
    request: Request,
    interactor: ListProductsDep,
    category_id: Optional[int] = Query(None),
    supplier_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: str = Query("popular", description="e.g., price_asc, newest"),
    in_stock: bool = Query(
        True, description="If true, only return products with stock_quantity > 0"
    ),
):
    """Retrieve a paginated, filtered, and sorted list of products.

    Extracts dynamic filter parameters from the query string beyond
    the known static parameters.

    Args:
        request: The incoming HTTP request (for dynamic query params).
        interactor: Injected list-products interactor.
        category_id: Optional category filter.
        supplier_id: Optional supplier filter.
        page: Page number (1-based).
        limit: Items per page (1-100).
        min_price: Optional minimum price filter.
        max_price: Optional maximum price filter.
        sort_by: Sort strategy name.

    Returns:
        A paginated product search response.
    """
    dynamic_filters: Dict[str, List[Any]] = {}
    for key, value in request.query_params.items():
        if key not in STATIC_PARAMS:
            raw_values = [v.strip() for v in value.split(",") if v.strip()]
            parsed_values = []
            for v in raw_values:
                if v.isdigit():
                    parsed_values.append(int(v))
                else:
                    parsed_values.append(v)
            if parsed_values:
                dynamic_filters[key] = parsed_values

    return await interactor.execute(
        category_id=category_id,
        supplier_id=supplier_id,
        page=page,
        limit=limit,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        dynamic_filters=dynamic_filters,
        in_stock=in_stock,
    )


FILTER_STATIC_PARAMS = {
    "category_id",
    "page",
    "limit",
    "min_price",
    "max_price",
    "in_stock",
}


@products_api.get(
    "/filters",
    status_code=status.HTTP_200_OK,
    response_model=GetCategoryFiltersResponse,
)
async def get_filter_options(
    request: Request,
    interactor: GetFiltersDep,
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    in_stock: bool = Query(True),
):
    """Retrieve available filter options for a category with product counts.

    Accepts currently applied filters to return accurate product counts
    per option. The frontend can use count=0 to disable unavailable options.

    Args:
        request: The incoming HTTP request (for dynamic query params).
        interactor: Injected get-filters interactor.
        category_id: The category to retrieve filters for.
        min_price: Current minimum price filter.
        max_price: Current maximum price filter.
        in_stock: Whether to count only in-stock products.

    Returns:
        A response containing grouped filter fields, options with counts, and brands.
    """
    brand_ids = None
    applied_option_ids = []

    for key, value in request.query_params.items():
        if key in FILTER_STATIC_PARAMS:
            continue
        raw_values = [v.strip() for v in value.split(",") if v.strip()]
        if not raw_values:
            continue

        if key.lower() in [a.lower() for a in settings.BRAND_FIELD_ALIASES]:
            brand_ids = [int(v) for v in raw_values if v.isdigit()]
        else:
            for v in raw_values:
                if v.isdigit():
                    applied_option_ids.append(int(v))

    return await interactor.execute(
        category_id=category_id,
        brand_ids=brand_ids,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        applied_option_ids=applied_option_ids if applied_option_ids else None,
    )


@products_api.get(
    "/search", status_code=status.HTTP_200_OK, response_model=ProductSearchResponse
)
async def search_products(
    request: Request,
    interactor: SearchProductsDep,
    q: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    in_stock: bool = Query(
        True, description="If true, only return products with stock_quantity > 0"
    ),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: Optional[str] = Query(
        None, description="e.g., price_asc, price_desc, newest"
    ),
):
    """Search products by text query with filtering and sorting.

    Combines full-text search with optional filters for category, price
    range, brand, and specification fields. Dynamic filter parameters
    beyond the known static set are parsed as specification filters.

    Args:
        request: The incoming HTTP request (for dynamic query params).
        interactor: Injected search-products interactor.
        q: The search query (minimum 2 characters).
        page: Page number (1-based).
        limit: Items per page (1-100).
        in_stock: If true, only return in-stock products.
        category_id: Optional category filter.
        min_price: Optional minimum price filter.
        max_price: Optional maximum price filter.
        sort_by: Optional sort strategy.

    Returns:
        A paginated product search response.
    """
    brand_ids = None
    spec_filters: Dict[str, List[Any]] = {}

    for key, value in request.query_params.items():
        if key in SEARCH_STATIC_PARAMS:
            continue
        raw_values = [v.strip() for v in value.split(",") if v.strip()]
        if not raw_values:
            continue

        if key.lower() in [a.lower() for a in settings.BRAND_FIELD_ALIASES]:
            brand_ids = [int(v) for v in raw_values if v.isdigit()]
        else:
            spec_filters[key] = raw_values

    return await interactor.execute(
        q,
        page,
        limit,
        in_stock=in_stock,
        category_id=category_id,
        brand_ids=brand_ids,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        spec_filters=spec_filters if spec_filters else None,
    )


@products_api.post(
    "/search/sync",
    status_code=status.HTTP_200_OK,
)
async def sync_products_to_search(
    search_repo: SearchRepoDep,
    db: AsyncSession = Depends(get_db),
    force: bool = Query(False, description="Force full re-sync instead of incremental"),
):
    from src.app.infra.search.sync import sync_all_products, sync_products_incremental
    from src.app.infra.redis.config import redis_client

    if force:
        await sync_all_products(db, search_repo)
        return {"status": "full sync complete"}

    result = await sync_products_incremental(db, search_repo, redis_client)
    return {"status": "incremental sync complete", **result}


@products_api.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetProductResponse,
)
async def get_product(product_id: int, interactor: GetProductDep):
    """Retrieve a single product by its ID.

    Args:
        product_id: The unique product identifier.
        interactor: Injected get-product interactor.

    Returns:
        A response containing the full product details.
    """
    return await interactor.execute(product_id)


internal_api = APIRouter(prefix="/internal/products", include_in_schema=False)


@internal_api.get("/availability/{product_id}")
async def get_product_availability_internal(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Internal endpoint to check a single product's availability.

    Args:
        product_id: The product ID to check.
        db: Injected database session.

    Returns:
        A dictionary with product ID, title, price, cover image, and stock.

    Raises:
        HTTPException: 404 if the product is not found or inactive.
    """
    from src.app.infra.database.models import ProductDb

    stmt = select(ProductDb).where(
        ProductDb.id == product_id,
        ProductDb.is_active == True,
        ProductDb.is_deleted == False,
    )
    result = await db.execute(stmt)
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {
        "id": p.id,
        "title": p.title,
        "price": float(p.price),
        "cover_image_url": p.cover_image_url,
        "stock_quantity": p.stock_quantity,
    }


@internal_api.post("/availability/batch")
async def get_products_availability_batch(
    product_ids: List[int] = Body(..., max_length=100),
    db: AsyncSession = Depends(get_db),
):
    """Internal endpoint to check availability of multiple products.

    Args:
        product_ids: List of product IDs to check (max 100).
        db: Injected database session.

    Returns:
        A list of product availability dictionaries.
    """
    from src.app.infra.database.models import ProductDb

    stmt = select(ProductDb).where(
        ProductDb.id.in_(product_ids),
        ProductDb.is_active == True,
        ProductDb.is_deleted == False,
    )
    result = await db.execute(stmt)
    products = result.scalars().all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "price": float(p.price),
            "cover_image_url": p.cover_image_url,
            "stock_quantity": p.stock_quantity,
        }
        for p in products
    ]


@internal_api.post("/suppliers/batch")
async def get_product_suppliers_batch(
    product_ids: List[int] = Body(..., max_length=100),
    db: AsyncSession = Depends(get_db),
):
    """Internal endpoint to get supplier IDs for multiple products.

    Args:
        product_ids: List of product IDs to look up (max 100).
        db: Injected database session.

    Returns:
        A list of product_id/supplier_id mappings.
    """
    from src.app.infra.database.models import ProductDb

    stmt = select(ProductDb.id, ProductDb.supplier_id).where(
        ProductDb.id.in_(product_ids),
        ProductDb.is_active == True,
        ProductDb.is_deleted == False,
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [{"product_id": row.id, "supplier_id": row.supplier_id} for row in rows]


@internal_api.post("/details/batch")
async def get_products_details_batch(
    product_ids: List[int] = Body(..., max_length=100),
    db: AsyncSession = Depends(get_db),
):
    """Internal endpoint to get full details for multiple products.

    Args:
        product_ids: List of product IDs to fetch (max 100).
        db: Injected database session.

    Returns:
        A list of detailed product dictionaries with brand and images.
    """
    from src.app.infra.database.models import ProductDb

    stmt = (
        select(ProductDb)
        .options(
            joinedload(ProductDb.brand),
            selectinload(ProductDb.images),
        )
        .where(
            ProductDb.id.in_(product_ids),
            ProductDb.is_active == True,
            ProductDb.is_deleted == False,
        )
    )
    result = await db.execute(stmt)
    products = result.unique().scalars().all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "price": float(p.price),
            "cover_image_url": p.cover_image_url,
            "stock_quantity": p.stock_quantity,
            "sku": p.sku,
            "brand": {"id": p.brand.id, "name": p.brand.name} if p.brand else None,
            "images": [img.image_url for img in p.images],
        }
        for p in products
    ]
