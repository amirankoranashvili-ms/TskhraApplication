import logging
from typing import Callable, Awaitable

from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.infra.broker.publisher import ProviderReplyPublisher
from src.app.infra.database.config import AsyncSessionLocal
from src.app.infra.database.repositories import (
    SqlAlchemyProductRepository,
    SqlAlchemySellerRepository,
    SqlAlchemyVerificationRequestRepository,
)
from src.app.core.interactors.handle_product_upload import HandleProductUploadInteractor
from src.app.core.interactors.handle_product_update import HandleProductUpdateInteractor

logger = logging.getLogger(__name__)

CATALOG_TOPIC = "catalog-events"


async def _handle_seller_created(db_session: AsyncSession, payload: dict) -> None:
    logger.info("Received seller creation request from Provider...")
    seller_repo = SqlAlchemySellerRepository(db_session)
    await seller_repo.create_seller(payload)
    logger.info(
        "Seller with supplier_id=%s created successfully.", payload.get("supplier_id")
    )

    vr_repo = SqlAlchemyVerificationRequestRepository(db_session)
    await vr_repo.create_verification_request(
        request_type="seller",
        supplier_id=payload["supplier_id"],
    )


async def _handle_seller_updated(db_session: AsyncSession, payload: dict) -> None:
    logger.info("Received seller update request from Provider...")
    seller_repo = SqlAlchemySellerRepository(db_session)
    await seller_repo.update_seller(payload)
    logger.info(
        "Seller with supplier_id=%s updated successfully.", payload.get("supplier_id")
    )

    vr_repo = SqlAlchemyVerificationRequestRepository(db_session)
    await vr_repo.create_verification_request(
        request_type="seller",
        supplier_id=payload["supplier_id"],
    )


async def _handle_product_created(db_session: AsyncSession, payload: dict) -> None:
    logger.info("Received product upload request from Provider...")
    repo = SqlAlchemyProductRepository(db_session)
    interactor = HandleProductUploadInteractor(repo)
    reply_payload = await interactor.execute(payload)

    if reply_payload["status"] == "SUCCESS":
        vr_repo = SqlAlchemyVerificationRequestRepository(db_session)
        await vr_repo.create_verification_request(
            request_type="product",
            supplier_id=payload.get("supplier_id"),
            product_id=reply_payload["product_id"],
        )

    await ProviderReplyPublisher.send_reply(
        status=reply_payload["status"], payload=reply_payload
    )


async def _handle_product_updated(db_session: AsyncSession, payload: dict) -> None:
    logger.info("Received product update request from Provider...")
    repo = SqlAlchemyProductRepository(db_session)
    interactor = HandleProductUpdateInteractor(repo)
    reply_payload = await interactor.execute(payload)

    if reply_payload["status"] == "SUCCESS":
        vr_repo = SqlAlchemyVerificationRequestRepository(db_session)
        await vr_repo.create_verification_request(
            request_type="product",
            supplier_id=reply_payload.get("supplier_id"),
            product_id=reply_payload["product_id"],
        )

    await ProviderReplyPublisher.send_reply(
        status=reply_payload["status"],
        payload=reply_payload,
        action="update",
    )


async def _handle_product_deleted(db_session: AsyncSession, payload: dict) -> None:
    logger.info("Received product deletion request from Provider...")
    repo = SqlAlchemyProductRepository(db_session)
    product_id = payload.get("product_id")
    supplier_id = payload.get("supplier_id")
    await repo.delete_product(product_id, supplier_id)
    logger.info("Product %s soft-deleted successfully.", product_id)


async def _handle_product_verified(db_session: AsyncSession, payload: dict) -> None:
    product_id = payload.get("product_id")
    status = payload.get("status")
    logger.info(
        "Received product.verified event: product_id=%s, status=%s", product_id, status
    )

    if status != "APPROVED" or not product_id:
        return

    repo = SqlAlchemyProductRepository(db_session)
    await repo._safe_sync_to_search(product_id)
    logger.info("Product %s synced to Elasticsearch after approval.", product_id)


EVENT_HANDLERS: dict[str, Callable[[AsyncSession, dict], Awaitable[None]]] = {
    "seller.created": _handle_seller_created,
    "seller.updated": _handle_seller_updated,
    "product.created": _handle_product_created,
    "product.updated": _handle_product_updated,
    "product.deleted": _handle_product_deleted,
    "product.verified": _handle_product_verified,
}


async def start_catalog_consumer(consumer: AIOKafkaConsumer) -> None:
    try:
        async for msg in consumer:
            payload = msg.value
            event_type = payload.get("event_type", "")

            handler = EVENT_HANDLERS.get(event_type)
            if not handler:
                logger.warning("No handler for event_type: %s", event_type)
                continue

            async with AsyncSessionLocal() as db_session:
                try:
                    await handler(db_session, payload)
                except Exception:
                    logger.exception(
                        "Error processing message: event_type=%s", event_type
                    )
    finally:
        await consumer.stop()
