import asyncio
import json
import logging
from typing import Awaitable, Callable
from uuid import UUID

from aiokafka import AIOKafkaConsumer
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.infra.database.config import AsyncSessionLocal
from src.app.infra.database.repositories import SqlAlchemyProductTaskRepository

logger = logging.getLogger(__name__)


async def _handle_rejection(db_session: AsyncSession, payload: dict) -> None:
    task_repo = SqlAlchemyProductTaskRepository(db_session)
    product_id = payload.get("product_id")
    error_message = payload.get("error_message", "Rejected by admin.")

    if product_id:
        logger.warning("Product %s rejected by Admin. Updating draft...", product_id)
        await task_repo.reject_task_by_product_id(
            product_id=product_id,
            error_message=error_message,
        )
    await db_session.commit()


async def _handle_success(db_session: AsyncSession, payload: dict) -> None:
    task_repo = SqlAlchemyProductTaskRepository(db_session)
    task_id_str = payload.get("task_id")
    product_id = payload.get("product_id")

    if not task_id_str:
        if product_id:
            logger.info("Product %s approved by admin.", product_id)
            task = await task_repo.get_task_by_product_id(product_id)
            if task:
                await task_repo.update_task_status(
                    task_id=task.task_id,
                    status="Completed",
                    product_id=product_id,
                )
        await db_session.commit()
        return

    task_id = UUID(task_id_str)
    logger.info("Task %s succeeded. Linking to Product %s...", task_id, product_id)
    await task_repo.update_task_status(
        task_id=task_id,
        status="Completed",
        product_id=product_id,
    )
    await db_session.commit()


async def _handle_failure(db_session: AsyncSession, payload: dict) -> None:
    task_repo = SqlAlchemyProductTaskRepository(db_session)
    task_id_str = payload.get("task_id")
    error_message = payload.get("error_message")

    if not task_id_str:
        await db_session.commit()
        return

    task_id = UUID(task_id_str)
    logger.warning("Task %s failed.", task_id)
    await task_repo.update_task_status(
        task_id=task_id,
        status="Failed",
        error_message=error_message,
    )
    await db_session.commit()


STATUS_HANDLERS: dict[str, Callable[[AsyncSession, dict], Awaitable[None]]] = {
    "product.upload.rejected": _handle_rejection,
    "product.update.rejected": _handle_rejection,
    "product.upload.success": _handle_success,
    "product.update.success": _handle_success,
    "product.upload.failed": _handle_failure,
    "product.update.failed": _handle_failure,
}


class VendorReplyConsumer:
    def __init__(self, bootstrap_servers: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            "product-replies",
            bootstrap_servers=self.bootstrap_servers,
            group_id="provider-replies",
            value_deserializer=lambda v: json.loads(v),
            key_deserializer=lambda k: k.decode() if k else None,
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume())

    async def _consume(self) -> None:
        try:
            async for msg in self._consumer:
                handler = STATUS_HANDLERS.get(msg.key)
                if not handler:
                    continue
                async with AsyncSessionLocal() as db_session:
                    try:
                        await handler(db_session, msg.value)
                    except Exception:
                        logger.exception("Failed to handle message key=%s", msg.key)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("VendorReplyConsumer crashed")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            await self._consumer.stop()
