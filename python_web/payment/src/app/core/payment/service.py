"""Application service encapsulating payment processing logic."""

import uuid
from decimal import Decimal
from typing import Any
from uuid import UUID

from backend_common.cache.service import CacheService

from src.app.core.payment.entities import (
    Payment,
    PaymentResult,
    PaymentStatus,
)
from src.app.core.payment.exceptions import (
    PaymentAlreadyCompletedException,
    PaymentFailedException,
    PaymentNotFoundException,
)
from src.app.core.payment.gateway import IPaymentGateway
from src.app.core.payment.repository import IPaymentRepository


class PaymentService:
    """Coordinates payment creation, charging via gateway, and refunds."""

    _REDIRECT_TTL = 300  # 5 minutes in seconds
    _CACHE_KEY_PREFIX = "redirect_url:"

    def __init__(
        self,
        payment_repository: IPaymentRepository,
        payment_gateway: IPaymentGateway,
        cache: CacheService,
    ) -> None:
        self.payment_repository = payment_repository
        self.payment_gateway = payment_gateway
        self.cache = cache

    async def process_payment(
        self,
        order_id: UUID,
        amount: Decimal,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[Payment, str | None]:
        cache_key = f"{self._CACHE_KEY_PREFIX}{order_id}"

        existing = await self.payment_repository.get_by_order_id(order_id)
        if existing and existing.status == PaymentStatus.COMPLETED:
            raise PaymentAlreadyCompletedException()
        if existing and existing.status == PaymentStatus.PENDING:
            cached_url = await self.cache.get(cache_key)
            if cached_url:
                return existing, cached_url
            # Cache expired — get a fresh redirect URL from gateway
            refresh_meta = dict(metadata or {})
            refresh_meta["payment_id"] = str(uuid.uuid4())
            refresh_meta.setdefault("order_id", str(order_id))
            result = await self.payment_gateway.charge(
                amount=amount, metadata=refresh_meta
            )
            if result.success and result.redirect_url:
                await self.cache.set(
                    cache_key, result.redirect_url, ttl=self._REDIRECT_TTL
                )
                if result.provider_payment_id:
                    await self.payment_repository.update_status(
                        existing.id, PaymentStatus.PENDING, result.provider_payment_id
                    )
            return existing, result.redirect_url if result.success else None

        payment = Payment(
            id=uuid.uuid4(),
            order_id=order_id,
            amount=amount,
            status=PaymentStatus.PENDING,
        )
        created = await self.payment_repository.create(payment)

        if metadata is None:
            metadata = {}
        metadata["payment_id"] = str(created.id)
        metadata.setdefault("order_id", str(order_id))

        result: PaymentResult = await self.payment_gateway.charge(
            amount=amount, metadata=metadata
        )

        if result.success:
            if result.redirect_url:
                await self.cache.set(
                    cache_key, result.redirect_url, ttl=self._REDIRECT_TTL
                )
            if result.requires_redirect:
                updated = await self.payment_repository.update_status(
                    created.id, PaymentStatus.PENDING, result.provider_payment_id
                )
            else:
                updated = await self.payment_repository.update_status(
                    created.id, PaymentStatus.COMPLETED, result.provider_payment_id
                )
            return updated or created, result.redirect_url
        else:
            await self.payment_repository.update_status(
                created.id, PaymentStatus.FAILED
            )
            raise PaymentFailedException(result.error_message)

    async def verify_payment(self, order_id: UUID) -> Payment:
        payment = await self.payment_repository.get_by_order_id(order_id)
        if not payment:
            raise PaymentNotFoundException()

        if payment.status == PaymentStatus.COMPLETED:
            return payment

        if not payment.provider_payment_id:
            return payment

        gateway_status = await self.payment_gateway.check_status(
            payment.provider_payment_id
        )

        if gateway_status != payment.status:
            updated = await self.payment_repository.update_status(
                payment.id, gateway_status
            )
            return updated or payment

        return payment

    async def get_payment_by_order(self, order_id: UUID) -> Payment | None:
        return await self.payment_repository.get_by_order_id(order_id)
