import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer
from pydantic import BaseModel, field_validator
from sqlalchemy import select

from src.app.core.constants import VerificationRequestType, VerificationStatus
from src.app.infra.database.models.products import VerificationRequestDb
from src.app.infra.database.session import async_session

logger = logging.getLogger(__name__)

PRODUCT_TOPIC = "product-events"


class VendorCreatedPayload(BaseModel):
    supplier_id: int

    @field_validator("supplier_id")
    @classmethod
    def supplier_id_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("supplier_id must be positive")
        return v


class VerificationConsumer:
    def __init__(self, bootstrap_servers: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            PRODUCT_TOPIC,
            bootstrap_servers=self.bootstrap_servers,
            group_id="admin-verification",
            value_deserializer=lambda v: json.loads(v),
            key_deserializer=lambda k: k.decode() if k else None,
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        self._task = asyncio.create_task(self._consume())

    async def _consume(self) -> None:
        try:
            async for msg in self._consumer:
                if msg.key != "seller.created":
                    continue

                try:
                    validated = VendorCreatedPayload.model_validate(msg.value)
                except ValueError as e:
                    logger.error("Invalid seller.created payload: %s", e)
                    continue

                async with async_session() as db_session:
                    existing = await db_session.execute(
                        select(VerificationRequestDb).where(
                            VerificationRequestDb.supplier_id == validated.supplier_id,
                            VerificationRequestDb.request_type == VerificationRequestType.SELLER.value,
                            VerificationRequestDb.status == VerificationStatus.PENDING.value,
                        )
                    )
                    if existing.scalar_one_or_none():
                        logger.info(
                            "Skipping duplicate seller verification for supplier_id=%s",
                            validated.supplier_id,
                        )
                        continue

                    verification_request = VerificationRequestDb(
                        request_type=VerificationRequestType.SELLER.value,
                        supplier_id=validated.supplier_id,
                        status=VerificationStatus.PENDING.value,
                    )
                    db_session.add(verification_request)
                    await db_session.commit()
                    logger.info(
                        "Admin: Created seller verification request for supplier_id=%s",
                        validated.supplier_id,
                    )
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("VerificationConsumer crashed")

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            await self._consumer.stop()
