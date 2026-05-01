import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.app.infra.database.models import (
    ProductDb as ProductORM,
    ProductFieldValueDb as ProductFieldValueORM,
)
from src.app.infra.search.repository import ElasticsearchProductRepository

logger = logging.getLogger(__name__)

SYNC_BATCH_SIZE = 500


def product_orm_to_search_document(product: ProductORM) -> dict:
    images = [img.image_url for img in product.images] if product.images else []
    cover = product.cover_image_url or (images[0] if images else None)

    spec_values = []
    spec_fields = {}
    if product.field_values:
        for fv in product.field_values:
            if fv.option:
                spec_values.append(fv.option.value)
                field_name = fv.field.name if fv.field else f"field_{fv.field_id}"
                spec_fields.setdefault(field_name, []).append(fv.option.value)

    return {
        "id": product.id,
        "title": product.title,
        "description": product.description or "",
        "price": float(product.price),
        "sku": product.sku,
        "category_id": product.category_id,
        "category_name": product.category.name if product.category else "",
        "brand_id": product.brand_id,
        "brand_name": product.brand.name if product.brand else "",
        "brand_logo_url": product.brand.logo_url if product.brand else None,
        "cover_image_url": cover,
        "stock_quantity": product.stock_quantity,
        "is_active": product.is_active,
        "is_deleted": product.is_deleted,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        "spec_values": spec_values,
        "spec_fields": spec_fields,
    }


async def sync_all_products(
    db_session: AsyncSession, search_repo: ElasticsearchProductRepository
):
    await search_repo.delete_all_documents()

    offset = 0
    total_synced = 0

    while True:
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
            .where(ProductORM.is_deleted == False)
            .order_by(ProductORM.id)
            .limit(SYNC_BATCH_SIZE)
            .offset(offset)
        )

        result = await db_session.execute(stmt)
        products = result.scalars().unique().all()

        if not products:
            break

        documents = [product_orm_to_search_document(p) for p in products]
        await search_repo.index_products_batch(documents)

        total_synced += len(documents)
        offset += SYNC_BATCH_SIZE
        logger.info("Synced %d products so far...", total_synced)

    logger.info("Full sync complete. Total products synced: %d", total_synced)


SYNC_KEY = "products:es_sync:last_sync_at"


def _build_sync_query(conditions: list):
    return (
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
        .where(*conditions)
        .order_by(ProductORM.id)
    )


async def sync_products_incremental(
    db_session: AsyncSession,
    search_repo: ElasticsearchProductRepository,
    redis_client,
) -> dict:
    last_sync_raw = await redis_client.get(SYNC_KEY)
    last_sync_at = (
        datetime.fromisoformat(last_sync_raw.decode()) if last_sync_raw else None
    )

    sync_started_at = datetime.now(timezone.utc)

    conditions = [ProductORM.is_deleted == False]
    if last_sync_at:
        conditions.append(ProductORM.updated_at > last_sync_at)

    offset = 0
    total_synced = 0

    while True:
        stmt = _build_sync_query(conditions).limit(SYNC_BATCH_SIZE).offset(offset)
        result = await db_session.execute(stmt)
        products = result.scalars().unique().all()

        if not products:
            break

        documents = [product_orm_to_search_document(p) for p in products]
        await search_repo.index_products_batch(documents)

        total_synced += len(documents)
        offset += SYNC_BATCH_SIZE
        logger.info("Incremental sync: %d products so far...", total_synced)

    deleted_count = 0
    if last_sync_at:
        del_stmt = select(ProductORM.id).where(
            ProductORM.is_deleted == True,
            ProductORM.updated_at > last_sync_at,
        )
        del_result = await db_session.execute(del_stmt)
        for (pid,) in del_result.all():
            await search_repo.delete_product_document(pid)
            deleted_count += 1

    await redis_client.set(SYNC_KEY, sync_started_at.isoformat())

    logger.info(
        "Incremental sync complete. Synced: %d, deleted: %d",
        total_synced,
        deleted_count,
    )
    return {"synced": total_synced, "deleted": deleted_count}
