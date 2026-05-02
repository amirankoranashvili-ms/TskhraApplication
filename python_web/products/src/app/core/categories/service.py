"""Category service layer.

Provides business logic for retrieving categories, their products,
and filter configurations, with optional Redis caching support.
"""

import json
from collections import defaultdict
from typing import Optional

from backend_common.cache.repository_cache import RepositoryCache

from src.app.core.categories.exceptions import CategoryNotFoundException
from src.app.core.categories.repository import (
    ICategoryRepository,
    ICategoryFieldRepository,
)
from src.app.core.schemas.category_schemas import (
    GetAllCategoriesResponse,
    GetCategoryFiltersResponse,
    CategoryFilterOut,
    FilterFieldOut,
    FieldOptionsOut,
    BrandFilterOut,
    GetCategoriesWithProductsResponse,
    CategoryWithProducts,
)
from src.app.core.products.mappers import map_domain_to_slim


class CategoryService:
    """Service for category-related business operations with optional caching."""

    CACHE_TTL = 1800  # 30 minutes

    def __init__(
        self,
        category_repository: ICategoryRepository,
        category_field_repository: ICategoryFieldRepository,
        cache: RepositoryCache | None = None,
    ) -> None:
        """Initialize with category repositories and an optional cache.

        Args:
            category_repository: Repository for category CRUD operations.
            category_field_repository: Repository for category field lookups.
            cache: Optional Redis-backed cache for category queries.
        """
        self.category_repository = category_repository
        self.category_field_repository = category_field_repository
        self.cache = cache

    async def get_categories(
        self, parent_id: Optional[int] = None
    ) -> GetAllCategoriesResponse:
        """Retrieve all categories, optionally filtered by parent.

        Args:
            parent_id: If provided, return only children of this category.

        Returns:
            Response containing the list of matching categories.
        """
        if self.cache:
            from src.app.core.categories.entities import Category

            categories = await self.cache.get_or_set_list(
                key=f"all:parent={parent_id}",
                loader=lambda: self.category_repository.get_all(parent_id),
                serializer=lambda cats: json.dumps(
                    [c.model_dump() for c in cats], default=str
                ),
                deserializer=lambda s: [Category(**c) for c in json.loads(s)],
                ttl=self.CACHE_TTL,
            )
            return GetAllCategoriesResponse(categories=categories)

        return GetAllCategoriesResponse(
            categories=await self.category_repository.get_all(parent_id)
        )

    async def get_categories_with_products(
        self, parent_id: Optional[int] = None, limit_per_cat: int = 4
    ) -> GetCategoriesWithProductsResponse:
        """Retrieve categories with their top products.

        Args:
            parent_id: If provided, return only children of this category.
            limit_per_cat: Maximum number of products per category.

        Returns:
            Response containing categories with embedded slim product lists.
        """
        domain_models = await self.category_repository.get_categories_with_top_products(
            limit_per_cat=limit_per_cat, parent_id=parent_id
        )

        final_categories = []
        for dm in domain_models:
            slim_products = [map_domain_to_slim(p) for p in dm.products]

            final_categories.append(
                CategoryWithProducts(
                    **dm.model_dump(exclude={"products"}), products=slim_products
                )
            )

        return GetCategoriesWithProductsResponse(categories=final_categories)

    async def get_filters(
        self,
        category_id: int,
        brand_ids: list[int] | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        in_stock: bool = True,
        applied_option_ids: list[int] | None = None,
    ) -> GetCategoryFiltersResponse:
        """Retrieve filter options for a category with product counts.

        Groups fields by their field group and returns available options
        with the number of matching products for each option.

        Args:
            category_id: The ID of the category to get filters for.
            brand_ids: Currently selected brand IDs.
            min_price: Current minimum price filter.
            max_price: Current maximum price filter.
            in_stock: Whether to count only in-stock products.
            applied_option_ids: Currently selected option IDs.

        Returns:
            Response containing grouped filter fields with counted options.

        Raises:
            CategoryNotFoundException: If the category does not exist.
        """
        category = await self.category_repository.get_by_id(category_id)
        if not category:
            raise CategoryNotFoundException()

        domain_models = (
            await self.category_field_repository.get_fields_and_options_for_category(
                category_id
            )
        )

        option_counts = await self.category_field_repository.get_option_product_counts(
            category_id=category_id,
            brand_ids=brand_ids,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            applied_option_ids=applied_option_ids,
        )

        brand_counts = await self.category_field_repository.get_brand_product_counts(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            applied_option_ids=applied_option_ids,
        )

        groups_dict = defaultdict(
            lambda: {"group_id": None, "group_name": "Ungrouped", "fields": []}
        )

        for cf in domain_models:
            field = cf.field
            g_id = field.group_id or 0

            if g_id != 0 and groups_dict[g_id]["group_id"] is None:
                groups_dict[g_id]["group_id"] = field.group.id if field.group else None
                groups_dict[g_id]["group_name"] = (
                    field.group.name if field.group else "Unknown"
                )

            if field.name not in groups_dict[g_id].get("_field_map", {}):
                groups_dict[g_id].setdefault("_field_map", {})[field.name] = (
                    FilterFieldOut(
                        field_id=field.id,
                        field_name=field.name,
                        is_required=cf.is_required,
                        options=[],
                    )
                )

            if cf.option:
                groups_dict[g_id]["_field_map"][field.name].options.append(
                    FieldOptionsOut(
                        option_id=cf.option.id,
                        option_value=cf.option.value,
                        product_count=option_counts.get(cf.option.id, 0),
                    )
                )

        brands_out = []
        for brand in category.brands:
            brands_out.append(
                BrandFilterOut(
                    brand_id=brand.id,
                    brand_name=brand.name,
                    logo_url=brand.logo_url,
                    product_count=brand_counts.get(brand.id, 0),
                )
            )

        return GetCategoryFiltersResponse(
            filters=[
                CategoryFilterOut(
                    group_id=data["group_id"],
                    group_name=data["group_name"],
                    fields=list(data.get("_field_map", {}).values()),
                )
                for data in groups_dict.values()
            ],
            brands=brands_out,
        )
