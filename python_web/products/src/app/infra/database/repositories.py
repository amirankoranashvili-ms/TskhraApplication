"""SQLAlchemy repository implementations.

Concrete implementations of the product, category, brand, seller,
and verification request repository interfaces using async SQLAlchemy.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, or_, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, aliased

from src.app.core.categories.entities import (
    Category,
    CategoryFieldDomainModel,
    CategoryWithProductsDomainModel,
)
from src.app.core.categories.repository import (
    ICategoryRepository,
    ICategoryFieldRepository,
)
from src.app.core.products.entities import Brand, ProductDomainModel, SortByOption
from src.app.core.products.repository import IProductRepository, IBrandRepository
from src.app.core.schemas.product_schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductSlim,
)
from src.app.infra.database.models import CategoryFieldDb as CategoryFieldORM
from src.app.infra.database.models import ProductImageDb as ProductImageORM
from src.app.infra.database.models import CategoryDb as CategoryORM
from src.app.infra.database.models import FieldDb as FieldORM
from src.app.infra.database.models import FieldOptionDb as FieldOptionORM
from src.app.infra.database.models import ProductFieldValueDb as ProductFieldValueORM
from src.app.infra.database.models import ProductDb as ProductORM
from src.app.infra.database.models import BrandDb as BrandORM
from src.app.infra.database.models import SupplierDb as SupplierORM
from src.app.infra.database.models import PlatformSellerDb as PlatformSellerORM
from src.app.infra.database.models import (
    VerificationRequestDb as VerificationRequestORM,
)

logger = logging.getLogger(__name__)
from src.app.infra.database.utils import (
    PriceAscSortHandler,
    PriceDescSortHandler,
    NewestSortHandler,
    PopularSortHandler,
)
from src.app.core.config import settings
from src.app.infra.search.sync import product_orm_to_search_document
from src.app.infra.search.client import get_elasticsearch_client, PRODUCTS_INDEX


class SqlAlchemyCategoryRepository(ICategoryRepository):
    """SQLAlchemy implementation of the category repository."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize with a database session.

        Args:
            db_session: The async SQLAlchemy session.
        """
        self.db_session = db_session

    async def get_all(self, parent_id: Optional[int] = None) -> List[Category]:
        """Retrieve all non-deleted categories with subcategory and product count info.

        Args:
            parent_id: If provided, return only children of this parent.

        Returns:
            A list of category entities.
        """
        SubCategoryORM = aliased(CategoryORM)
        has_children_subq = (
            select(SubCategoryORM.id)
            .where(
                SubCategoryORM.parent_id == CategoryORM.id,
                SubCategoryORM.is_deleted == False,
            )
            .exists()
        )

        product_count_subq = (
            select(func.count(ProductORM.id))
            .where(
                ProductORM.category_id == CategoryORM.id,
                ProductORM.is_active == True,
                ProductORM.is_deleted == False,
            )
            .correlate(CategoryORM)
            .scalar_subquery()
        )

        stmt = select(
            CategoryORM,
            has_children_subq.label("has_subcategories"),
            product_count_subq.label("product_count"),
        ).where(CategoryORM.is_deleted == False)

        if parent_id is not None:
            stmt = stmt.where(CategoryORM.parent_id == parent_id)
        else:
            stmt = stmt.where(CategoryORM.parent_id.is_(None))

        result = await self.db_session.execute(stmt)

        rows = result.all()

        categories = []
        for orm_category, has_subcategories, product_count in rows:
            cat_dict = {
                "id": orm_category.id,
                "parent_id": orm_category.parent_id,
                "name": orm_category.name,
                "slug": orm_category.slug,
                "image_url": orm_category.image_url,
                "has_subcategories": has_subcategories,
                "product_count": product_count or 0,
            }
            categories.append(Category(**cat_dict))

        return categories

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Retrieve a single category by ID with brand associations.

        Args:
            category_id: The unique category identifier.

        Returns:
            The category entity, or None if not found.
        """
        SubCategoryORM = aliased(CategoryORM)
        has_children_subq = (
            select(SubCategoryORM.id)
            .where(
                SubCategoryORM.parent_id == CategoryORM.id,
                SubCategoryORM.is_deleted == False,
            )
            .exists()
        )

        stmt = (
            select(CategoryORM, has_children_subq.label("has_subcategories"))
            .options(selectinload(CategoryORM.brands))
            .where(CategoryORM.id == category_id, CategoryORM.is_deleted == False)
        )

        result = await self.db_session.execute(stmt)
        row = result.first()

        if not row:
            return None

        orm_category, has_subcategories = row
        cat_dict = {
            "id": orm_category.id,
            "parent_id": orm_category.parent_id,
            "name": orm_category.name,
            "slug": orm_category.slug,
            "image_url": orm_category.image_url,
            "has_subcategories": has_subcategories,
            "brands": [Brand.model_validate(b) for b in orm_category.brands],
        }

        return Category(**cat_dict)

    async def get_categories_with_top_products(
        self,
        limit_per_cat: int,
        parent_id: Optional[int] = None,
    ) -> List[CategoryWithProductsDomainModel]:
        """Retrieve categories with their N most recent products.

        Args:
            limit_per_cat: Maximum products per category.
            parent_id: If provided, filter by parent category.

        Returns:
            A list of categories with embedded product domain models.
        """
        SubCategoryORM = aliased(CategoryORM)
        has_children_subq = (
            select(SubCategoryORM.id)
            .where(
                SubCategoryORM.parent_id == CategoryORM.id,
                SubCategoryORM.is_deleted == False,
            )
            .exists()
        )

        product_count_subq = (
            select(func.count(ProductORM.id))
            .where(
                ProductORM.category_id == CategoryORM.id,
                ProductORM.is_active == True,
                ProductORM.is_deleted == False,
            )
            .correlate(CategoryORM)
            .scalar_subquery()
        )

        rank_stmt = (
            select(
                ProductORM,
                func.row_number()
                .over(
                    partition_by=ProductORM.category_id,
                    order_by=ProductORM.created_at.desc(),
                )
                .label("rn"),
            ).where(ProductORM.is_active == True, ProductORM.is_deleted == False)
        ).subquery()

        product_alias = aliased(ProductORM, rank_stmt)

        stmt = (
            select(
                CategoryORM,
                has_children_subq.label("has_subcategories"),
                product_count_subq.label("product_count"),
                product_alias,
            )
            .outerjoin(
                product_alias,
                (product_alias.category_id == CategoryORM.id)
                & (rank_stmt.c.rn <= limit_per_cat),
            )
            .where(CategoryORM.is_deleted == False)
            .options(
                joinedload(product_alias.brand),
                joinedload(product_alias.category).joinedload(CategoryORM.parent),
                selectinload(product_alias.images),
                selectinload(product_alias.field_values)
                .joinedload(ProductFieldValueORM.option)
                .joinedload(FieldOptionORM.field)
                .joinedload(FieldORM.group),
            )
        )

        if parent_id is not None:
            stmt = stmt.where(CategoryORM.parent_id == parent_id)
        else:
            stmt = stmt.where(CategoryORM.parent_id.is_(None))

        result = await self.db_session.execute(stmt)
        rows = result.all()

        categories_map = {}

        for cat_orm, has_subcategories, product_count, prod_orm in rows:
            if cat_orm.id not in categories_map:
                categories_map[cat_orm.id] = CategoryWithProductsDomainModel(
                    id=cat_orm.id,
                    parent_id=cat_orm.parent_id,
                    name=cat_orm.name,
                    slug=cat_orm.slug,
                    image_url=cat_orm.image_url,
                    has_subcategories=has_subcategories,
                    product_count=product_count or 0,
                    products=[],
                )

            if prod_orm:
                product_domain = ProductDomainModel.model_validate(prod_orm)
                categories_map[cat_orm.id].products.append(product_domain)

        return list(categories_map.values())


class SqlAlchemyCategoryFieldRepository(ICategoryFieldRepository):
    """SQLAlchemy implementation of the category field repository."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize with a database session.

        Args:
            db_session: The async SQLAlchemy session.
        """
        self.db_session = db_session

    async def get_fields_and_options_for_category(
        self, category_id: int
    ) -> List[CategoryFieldDomainModel]:
        """Retrieve all fields and options for a category with eager loading.

        Args:
            category_id: The category to fetch fields for.

        Returns:
            A list of category field domain models.
        """
        stmt = (
            select(CategoryFieldORM)
            .join(CategoryFieldORM.field)
            .outerjoin(FieldORM.group)
            .options(
                joinedload(CategoryFieldORM.field).joinedload(FieldORM.group),
                joinedload(CategoryFieldORM.option),
            )
            .where(CategoryFieldORM.category_id == category_id)
        )

        result = await self.db_session.execute(stmt)
        orm_results = result.unique().scalars().all()

        return [CategoryFieldDomainModel.model_validate(item) for item in orm_results]

    async def get_option_product_counts(
        self,
        category_id: int,
        brand_ids: Optional[List[int]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: bool = True,
        applied_option_ids: Optional[List[int]] = None,
    ) -> Dict[int, int]:
        """Count products per filter option with current filters applied.

        For each option_id in the category, returns the number of active
        products that match the given filters AND have that option.

        Args:
            category_id: The category to count within.
            brand_ids: Currently selected brand IDs.
            min_price: Current minimum price filter.
            max_price: Current maximum price filter.
            in_stock: Whether to count only in-stock products.
            applied_option_ids: Currently selected option IDs from other filters.

        Returns:
            A dict mapping option_id to product count.
        """
        conditions = [
            ProductORM.category_id == category_id,
            ProductORM.is_active == True,
            ProductORM.is_deleted == False,
        ]
        if in_stock:
            conditions.append(ProductORM.stock_quantity > 0)
        if brand_ids:
            conditions.append(ProductORM.brand_id.in_(brand_ids))
        if min_price is not None:
            conditions.append(ProductORM.price >= min_price)
        if max_price is not None:
            conditions.append(ProductORM.price <= max_price)

        if applied_option_ids:
            applied_subq = (
                select(ProductFieldValueORM.product_id)
                .where(ProductFieldValueORM.option_id.in_(applied_option_ids))
                .group_by(ProductFieldValueORM.product_id)
            ).subquery()
            conditions.append(ProductORM.id.in_(select(applied_subq.c.product_id)))

        stmt = (
            select(
                ProductFieldValueORM.option_id,
                func.count(func.distinct(ProductFieldValueORM.product_id)),
            )
            .join(ProductORM, ProductFieldValueORM.product_id == ProductORM.id)
            .where(*conditions)
            .group_by(ProductFieldValueORM.option_id)
        )

        result = await self.db_session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    async def get_brand_product_counts(
        self,
        category_id: int,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: bool = True,
        applied_option_ids: Optional[List[int]] = None,
    ) -> Dict[int, int]:
        """Count products per brand with current spec filters applied.

        Args:
            category_id: The category to count within.
            min_price: Current minimum price filter.
            max_price: Current maximum price filter.
            in_stock: Whether to count only in-stock products.
            applied_option_ids: Currently selected option IDs.

        Returns:
            A dict mapping brand_id to product count.
        """
        conditions = [
            ProductORM.category_id == category_id,
            ProductORM.is_active == True,
            ProductORM.is_deleted == False,
        ]
        if in_stock:
            conditions.append(ProductORM.stock_quantity > 0)
        if min_price is not None:
            conditions.append(ProductORM.price >= min_price)
        if max_price is not None:
            conditions.append(ProductORM.price <= max_price)

        if applied_option_ids:
            applied_subq = (
                select(ProductFieldValueORM.product_id)
                .where(ProductFieldValueORM.option_id.in_(applied_option_ids))
                .group_by(ProductFieldValueORM.product_id)
            ).subquery()
            conditions.append(ProductORM.id.in_(select(applied_subq.c.product_id)))

        stmt = (
            select(ProductORM.brand_id, func.count(ProductORM.id))
            .where(*conditions)
            .group_by(ProductORM.brand_id)
        )

        result = await self.db_session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}


class SqlAlchemyProductRepository(IProductRepository):
    """SQLAlchemy implementation of the product repository.

    Handles product CRUD, search, filtering, and Elasticsearch synchronization.
    """

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize with a database session and sort handler chain.

        Args:
            db_session: The async SQLAlchemy session.
        """
        self.db_session = db_session
        self.sort_chain = PriceAscSortHandler()
        self.sort_chain.set_next(PriceDescSortHandler()).set_next(
            NewestSortHandler()
        ).set_next(PopularSortHandler())

    async def _safe_sync_to_search(self, product_id: int) -> None:
        try:
            await self._sync_product_to_search(product_id)
        except Exception as e:
            logger.warning(
                "Failed to sync product %s to Elasticsearch: %s", product_id, e
            )

    async def _load_product(
        self, product_id: int, include_deleted: bool = False
    ) -> ProductORM:
        """Load a product ORM instance by ID.

        Args:
            product_id: The product ID to load.
            include_deleted: If True, include soft-deleted products.

        Returns:
            The product ORM instance.

        Raises:
            ValueError: If the product is not found.
        """
        stmt = select(ProductORM).options(
            selectinload(ProductORM.images),
            selectinload(ProductORM.field_values),
        )
        if not include_deleted:
            stmt = stmt.where(
                ProductORM.id == product_id, ProductORM.is_deleted == False
            )
        else:
            stmt = stmt.where(ProductORM.id == product_id)
        result = await self.db_session.execute(stmt)
        product = result.scalar_one_or_none()
        if not product:
            raise ValueError(f"Product with id {product_id} not found.")
        return product

    async def _apply_product_updates(
        self, product: ProductORM, product_data, is_provider: bool = False
    ) -> None:
        """Apply update fields to a product ORM, including images and specs.

        Args:
            product: The product ORM instance to update.
            product_data: The update request with fields to apply.
            is_provider: If True, brand_id is an option_id that needs resolving.
        """
        if product_data.category_id is not None:
            product.category_id = product_data.category_id
        if product_data.brand_id is not None:
            brand_id = product_data.brand_id
            if is_provider:
                brand_id = await self._resolve_brand_id_from_option(brand_id)
            product.brand_id = brand_id
        if product_data.title is not None:
            product.title = product_data.title
        if product_data.description is not None:
            product.description = product_data.description
        if product_data.price is not None:
            product.price = product_data.price
        if product_data.stock_quantity is not None:
            product.stock_quantity = product_data.stock_quantity
        if product_data.cover_image_url is not None:
            product.cover_image_url = product_data.cover_image_url or None

        if product_data.deleted_images:
            del_stmt = delete(ProductImageORM).where(
                ProductImageORM.product_id == product.id,
                ProductImageORM.image_url.in_(product_data.deleted_images),
            )
            await self.db_session.execute(del_stmt)

        if product_data.images:
            for img_url in product_data.images:
                self.db_session.add(
                    ProductImageORM(product_id=product.id, image_url=img_url)
                )

        if product_data.specifications is not None:
            del_specs = delete(ProductFieldValueORM).where(
                ProductFieldValueORM.product_id == product.id,
            )
            await self.db_session.execute(del_specs)
            for spec in product_data.specifications:
                self.db_session.add(
                    ProductFieldValueORM(
                        product_id=product.id,
                        field_id=spec.field_id,
                        option_id=spec.option_id,
                    )
                )

        product.is_active = False

    async def _resolve_brand_id_from_option(self, option_id: int) -> int:
        """Resolve a brand ID from a field option ID.

        Looks up the option value (brand name) and finds or creates
        the corresponding brand in the brands table.

        Args:
            option_id: The field_options ID containing the brand name.

        Returns:
            The actual brand ID from the brands table.
        """
        option = await self.db_session.get(FieldOptionORM, option_id)
        if not option:
            return option_id

        brand_name = option.value.strip()
        stmt = select(BrandORM).where(
            BrandORM.name == brand_name,
            BrandORM.is_deleted == False,
        )
        result = await self.db_session.execute(stmt)
        brand = result.scalar_one_or_none()

        if brand:
            return brand.id

        new_brand = BrandORM(name=brand_name)
        self.db_session.add(new_brand)
        await self.db_session.flush()
        return new_brand.id

    async def create_product(
        self, product_data: ProductCreateRequest, is_provider: bool
    ) -> ProductDomainModel:
        """Create a new product with images and specifications.

        Args:
            product_data: The product creation request payload.
            is_provider: Whether the creator is a provider.

        Returns:
            The created product domain model.
        """
        brand_id = product_data.brand_id
        if is_provider:
            brand_id = await self._resolve_brand_id_from_option(brand_id)

        new_product = ProductORM(
            category_id=product_data.category_id,
            supplier_id=product_data.supplier_id,
            brand_id=brand_id,
            cover_image_url=product_data.cover_image_url,
            title=product_data.title,
            description=product_data.description,
            price=product_data.price,
            sku=product_data.sku,
            stock_quantity=product_data.stock_quantity,
            is_active=False,
            is_scrapped=not is_provider,
        )

        self.db_session.add(new_product)
        await self.db_session.flush()

        for img_url in product_data.images:
            new_image = ProductImageORM(product_id=new_product.id, image_url=img_url)
            self.db_session.add(new_image)

        for spec in product_data.specifications:
            new_spec = ProductFieldValueORM(
                product_id=new_product.id,
                field_id=spec.field_id,
                option_id=spec.option_id,
            )
            self.db_session.add(new_spec)

        await self.db_session.commit()

        created = await self._get_by_id_internal(new_product.id)

        await self._safe_sync_to_search(new_product.id)

        return created

    async def update_product(
        self,
        product_id: int,
        product_data: ProductUpdateRequest,
        is_provider: bool = False,
    ) -> None:
        product = await self._load_product(product_id, include_deleted=False)
        await self._apply_product_updates(product, product_data, is_provider)
        await self.db_session.commit()
        await self._safe_sync_to_search(product_id)

    async def reactivate_rejected_product(
        self,
        product_id: int,
        product_data: ProductUpdateRequest,
        is_provider: bool = False,
    ) -> None:
        """Reactivate a rejected product with updated data.

        Args:
            product_id: The ID of the product to reactivate.
            product_data: The updated product fields.
            is_provider: If True, brand_id is an option_id that needs resolving.
        """
        product = await self._load_product(product_id, include_deleted=True)
        await self._apply_product_updates(product, product_data, is_provider)
        product.is_deleted = False
        await self.db_session.commit()
        await self._safe_sync_to_search(product_id)

    async def delete_product(self, product_id: int, supplier_id: int) -> None:
        stmt = select(ProductORM).where(
            ProductORM.id == product_id,
            ProductORM.supplier_id == supplier_id,
            ProductORM.is_deleted == False,
        )
        result = await self.db_session.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            raise ValueError(
                f"Product with id {product_id} and supplier_id {supplier_id} not found."
            )

        product.is_deleted = True
        product.is_active = False
        await self.db_session.commit()

        try:
            client = get_elasticsearch_client()
            await client.delete(index=PRODUCTS_INDEX, id=str(product_id))
            await client.close()
        except Exception as e:
            logger.warning(
                "Failed to delete product %s from Elasticsearch: %s", product_id, e
            )

    async def get_by_id(self, product_id: int) -> Optional[ProductDomainModel]:
        """Retrieve an active, non-deleted product by ID with all relationships.

        Args:
            product_id: The unique product identifier.

        Returns:
            The product domain model, or None if not found.
        """
        stmt = (
            select(ProductORM)
            .options(
                selectinload(ProductORM.images),
                joinedload(ProductORM.brand),
                joinedload(ProductORM.category).joinedload(CategoryORM.parent),
                selectinload(ProductORM.field_values)
                .joinedload(ProductFieldValueORM.option)
                .joinedload(FieldOptionORM.field)
                .joinedload(FieldORM.group),
            )
            .where(
                ProductORM.id == product_id,
                ProductORM.is_deleted == False,
                ProductORM.is_active == True,
            )
        )

        result = await self.db_session.execute(stmt)
        orm_product = result.unique().scalar_one_or_none()

        if not orm_product:
            return None

        return ProductDomainModel.model_validate(orm_product)

    async def _get_by_id_internal(
        self, product_id: int
    ) -> Optional[ProductDomainModel]:
        """Retrieve a non-deleted product by ID regardless of active status.

        Args:
            product_id: The unique product identifier.

        Returns:
            The product domain model, or None if not found.
        """
        stmt = (
            select(ProductORM)
            .options(
                selectinload(ProductORM.images),
                joinedload(ProductORM.brand),
                joinedload(ProductORM.category).joinedload(CategoryORM.parent),
                selectinload(ProductORM.field_values)
                .joinedload(ProductFieldValueORM.option)
                .joinedload(FieldOptionORM.field)
                .joinedload(FieldORM.group),
            )
            .where(
                ProductORM.id == product_id,
                ProductORM.is_deleted == False,
            )
        )

        result = await self.db_session.execute(stmt)
        orm_product = result.unique().scalar_one_or_none()

        if not orm_product:
            return None

        return ProductDomainModel.model_validate(orm_product)

    async def _sync_product_to_search(self, product_id: int) -> None:
        stmt = (
            select(ProductORM)
            .options(
                joinedload(ProductORM.brand),
                joinedload(ProductORM.category),
                selectinload(ProductORM.images),
                selectinload(ProductORM.field_values).joinedload(
                    ProductFieldValueORM.option
                ),
                selectinload(ProductORM.field_values).joinedload(
                    ProductFieldValueORM.field
                ),
            )
            .where(ProductORM.id == product_id)
        )
        result = await self.db_session.execute(stmt)
        product = result.scalar_one_or_none()
        if not product:
            return

        document = product_orm_to_search_document(product)
        client = get_elasticsearch_client()
        try:
            await client.index(index=PRODUCTS_INDEX, id=str(product_id), document=document)
        finally:
            await client.close()

    async def search_products(
        self, q: str, limit: int, offset: int, *, in_stock: bool = True
    ) -> Tuple[List[ProductSlim], int]:
        """Search products by title, description, or SKU using SQL ILIKE.

        Args:
            q: The search query string.
            limit: Maximum number of results.
            offset: Number of results to skip.

        Returns:
            A tuple of (matching products, total count).
        """
        search_condition = or_(
            ProductORM.title.ilike(f"%{q}%"),
            ProductORM.description.ilike(f"%{q}%"),
            ProductORM.sku.ilike(f"%{q}%"),
        )

        conditions = [
            ProductORM.is_deleted == False,
            ProductORM.is_active == True,
            search_condition,
        ]

        if in_stock:
            conditions.append(ProductORM.stock_quantity > 0)

        count_stmt = select(func.count()).select_from(ProductORM).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total_count = count_result.scalar() or 0

        stmt = (
            select(ProductORM)
            .options(
                selectinload(ProductORM.images),
                joinedload(ProductORM.brand),
            )
            .where(*conditions)
            .limit(limit)
            .offset(offset)
        )

        result = await self.db_session.execute(stmt)
        orm_products = result.scalars().all()

        domain_models = [ProductSlim.model_validate(p) for p in orm_products]

        return domain_models, total_count

    async def get_products(
        self,
        category_id: Optional[int],
        supplier_id: Optional[int],
        limit: int,
        offset: int,
        min_price: Optional[float],
        max_price: Optional[float],
        sort_by: SortByOption,
        dynamic_filters: Dict[str, List[Any]],
        in_stock: bool = True,
    ) -> Tuple[List[ProductSlim], int]:
        """Retrieve filtered, sorted, and paginated products.

        Applies static filters (category, supplier, price range) and dynamic
        field-based filters including brand alias handling.

        Args:
            category_id: Optional category filter.
            supplier_id: Optional supplier filter.
            limit: Maximum number of products.
            offset: Number of products to skip.
            min_price: Optional minimum price.
            max_price: Optional maximum price.
            sort_by: Sorting strategy.
            dynamic_filters: Additional field-based filters.

        Returns:
            A tuple of (product list, total count).
        """

        conditions = [ProductORM.is_deleted == False, ProductORM.is_active == True]

        if in_stock:
            conditions.append(ProductORM.stock_quantity > 0)

        if category_id is not None:
            conditions.append(ProductORM.category_id == category_id)

        if supplier_id is not None:
            conditions.append(ProductORM.supplier_id == supplier_id)

        if min_price is not None:
            conditions.append(ProductORM.price >= min_price)

        if max_price is not None:
            conditions.append(ProductORM.price <= max_price)

        for key, option_ids in dynamic_filters.items():
            if not option_ids:
                continue

            if key.lower() in settings.BRAND_FIELD_ALIASES:
                conditions.append(ProductORM.brand_id.in_(option_ids))
            else:
                subq = (
                    select(ProductFieldValueORM.id)
                    .where(
                        ProductFieldValueORM.product_id == ProductORM.id,
                        ProductFieldValueORM.option_id.in_(option_ids),
                    )
                    .exists()
                )
                conditions.append(subq)

        count_stmt = select(func.count()).select_from(ProductORM).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total_count = count_result.scalar() or 0

        stmt = (
            select(ProductORM)
            .options(
                selectinload(ProductORM.images),
                joinedload(ProductORM.brand),
            )
            .where(*conditions)
        )

        stmt = self.sort_chain.handle(stmt, sort_by)

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db_session.execute(stmt)
        orm_products = result.scalars().all()

        domain_models = [ProductSlim.model_validate(p) for p in orm_products]

        return domain_models, total_count


class SqlAlchemyBrandRepository(IBrandRepository):
    """SQLAlchemy implementation of the brand repository."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize with a database session.

        Args:
            db_session: The async SQLAlchemy session.
        """
        self.db_session = db_session

    async def get_by_id(self, brand_id: int) -> Optional[Brand]:
        """Retrieve a non-deleted brand by its ID.

        Args:
            brand_id: The unique brand identifier.

        Returns:
            The brand entity, or None if not found.
        """
        stmt = select(BrandORM).where(
            BrandORM.id == brand_id, BrandORM.is_deleted == False
        )

        result = await self.db_session.execute(stmt)

        orm_brand = result.scalar_one_or_none()

        if not orm_brand:
            return None

        return Brand.model_validate(orm_brand)


class SqlAlchemySellerRepository:
    """SQLAlchemy repository for supplier and platform seller operations."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize with a database session.

        Args:
            db_session: The async SQLAlchemy session.
        """
        self.db_session = db_session

    async def create_seller(self, seller_data: dict) -> None:
        """Create a new supplier and platform seller record.

        Args:
            seller_data: Dictionary containing supplier_id, name, user_id,
                identification_number, legal_address, and optional contact fields.
        """
        supplier = SupplierORM(
            id=seller_data["supplier_id"],
            name=seller_data["name"],
            supplier_type="internal",
        )
        self.db_session.add(supplier)
        await self.db_session.flush()

        platform_seller = PlatformSellerORM(
            supplier_id=seller_data["supplier_id"],
            user_id=UUID(seller_data["user_id"]),
            identification_number=seller_data["identification_number"],
            legal_address=seller_data["legal_address"],
            contact_phone=seller_data.get("contact_phone"),
            contact_email=seller_data.get("contact_email"),
            bank_account_number=seller_data.get("bank_account_number"),
        )
        self.db_session.add(platform_seller)
        await self.db_session.commit()
        logger.info(
            f"Created supplier and platform seller with supplier_id={seller_data['supplier_id']}"
        )

    async def update_seller(self, seller_data: dict) -> None:
        """Update an existing supplier and platform seller record.

        Args:
            seller_data: Dictionary containing supplier_id, name, and updated fields.
        """
        supplier_id = seller_data["supplier_id"]

        stmt = (
            update(SupplierORM)
            .where(SupplierORM.id == supplier_id)
            .values(name=seller_data["name"], is_deleted=False)
        )
        await self.db_session.execute(stmt)

        stmt = (
            update(PlatformSellerORM)
            .where(PlatformSellerORM.supplier_id == supplier_id)
            .values(
                identification_number=seller_data["identification_number"],
                legal_address=seller_data["legal_address"],
                contact_phone=seller_data.get("contact_phone"),
                contact_email=seller_data.get("contact_email"),
                bank_account_number=seller_data.get("bank_account_number"),
            )
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
        logger.info(f"Updated seller with supplier_id={supplier_id}")


class SqlAlchemyVerificationRequestRepository:
    """SQLAlchemy repository for verification request operations."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize with a database session.

        Args:
            db_session: The async SQLAlchemy session.
        """
        self.db_session = db_session

    async def create_verification_request(
        self,
        request_type: str,
        supplier_id: int,
        product_id: Optional[int] = None,
    ) -> None:
        """Create a new verification request for a product or seller.

        Args:
            request_type: The type of request (e.g., "product", "seller").
            supplier_id: The supplier associated with the request.
            product_id: Optional product ID for product verification requests.
        """
        vr = VerificationRequestORM(
            request_type=request_type,
            supplier_id=supplier_id,
            product_id=product_id,
        )
        self.db_session.add(vr)
        await self.db_session.commit()
        logger.info(
            f"Created verification request: type={request_type}, supplier_id={supplier_id}, product_id={product_id}"
        )
