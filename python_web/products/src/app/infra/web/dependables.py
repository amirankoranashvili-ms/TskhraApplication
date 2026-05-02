"""FastAPI dependency injection factories.

Provides dependency functions and type aliases for injecting services,
interactors, and repositories into API route handlers.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend_common.cache.repository_cache import RepositoryCache

from src.app.core.categories.service import CategoryService
from src.app.core.config import settings
from src.app.core.interactors.get_filters import GetFiltersInteractor
from src.app.core.interactors.get_product import GetProductInteractor
from src.app.core.interactors.list_products import ListProductsInteractor
from src.app.core.interactors.search_products import SearchProductsInteractor
from src.app.core.products.service import ProductService
from src.app.infra.database.config import get_db
from src.app.infra.database.repositories import (
    SqlAlchemyCategoryRepository,
    SqlAlchemyProductRepository,
    SqlAlchemyCategoryFieldRepository,
)
from src.app.infra.redis.config import redis_client
from src.app.infra.search.client import get_elasticsearch_client
from src.app.infra.search.repository import ElasticsearchProductRepository


async def get_search_repo() -> ElasticsearchProductRepository:
    client = get_elasticsearch_client()
    return ElasticsearchProductRepository(client)


SearchRepoDep = Annotated[
    ElasticsearchProductRepository, Depends(get_search_repo)
]


def _build_product_service(db: AsyncSession) -> ProductService:
    """Build a ProductService with its repository wired to the given session.

    Args:
        db: The async database session.

    Returns:
        A configured ProductService instance.
    """
    repository = SqlAlchemyProductRepository(db)
    return ProductService(repository)


def _build_category_service(db: AsyncSession) -> CategoryService:
    """Build a CategoryService with repositories and cache wired to the session.

    Args:
        db: The async database session.

    Returns:
        A configured CategoryService instance with Redis caching.
    """
    category_repository = SqlAlchemyCategoryRepository(db)
    category_field_repository = SqlAlchemyCategoryFieldRepository(db)
    cache = RepositoryCache(client=redis_client, prefix="products:categories", ttl=1800)
    return CategoryService(category_repository, category_field_repository, cache=cache)


# --- Service deps (for endpoints that need direct service access) ---


async def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    """FastAPI dependency that provides a ProductService instance."""
    return _build_product_service(db)


async def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    """FastAPI dependency that provides a CategoryService instance."""
    return _build_category_service(db)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]


# --- Interactor deps ---


async def get_product_interactor(
    db: AsyncSession = Depends(get_db),
) -> GetProductInteractor:
    """FastAPI dependency that provides a GetProductInteractor instance."""
    return GetProductInteractor(product_service=_build_product_service(db))


async def get_list_products_interactor(
    db: AsyncSession = Depends(get_db),
) -> ListProductsInteractor:
    """FastAPI dependency that provides a ListProductsInteractor instance."""
    return ListProductsInteractor(product_service=_build_product_service(db))


async def get_search_products_interactor(
    db: AsyncSession = Depends(get_db),
    search_repo: ElasticsearchProductRepository = Depends(get_search_repo),
) -> SearchProductsInteractor:
    return SearchProductsInteractor(
        product_service=_build_product_service(db),
        search_repository=search_repo,
    )


async def get_filters_interactor(
    db: AsyncSession = Depends(get_db),
) -> GetFiltersInteractor:
    """FastAPI dependency that provides a GetFiltersInteractor instance."""
    return GetFiltersInteractor(category_service=_build_category_service(db))


GetProductDep = Annotated[GetProductInteractor, Depends(get_product_interactor)]
ListProductsDep = Annotated[
    ListProductsInteractor, Depends(get_list_products_interactor)
]
SearchProductsDep = Annotated[
    SearchProductsInteractor, Depends(get_search_products_interactor)
]
GetFiltersDep = Annotated[GetFiltersInteractor, Depends(get_filters_interactor)]
