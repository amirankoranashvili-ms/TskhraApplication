"""Stripe payment gateway placeholder.

Will be fully implemented when Stripe API keys are available.
"""

import logging
from decimal import Decimal
from typing import Any

from src.app.core.payment.entities import PaymentResult, PaymentStatus

logger = logging.getLogger(__name__)


class StripePaymentGateway:
    """Stripe payment gateway (placeholder, not yet functional)."""

    def __init__(self, secret_key: str) -> None:
        """Initialize with a Stripe secret key.

        Args:
            secret_key: The Stripe API secret key.
        """
        self.secret_key = secret_key

    async def charge(
        self,
        amount: Decimal,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentResult:
        """Charge via Stripe (not yet implemented).

        Args:
            amount: The amount to charge in dollars.
            metadata: Optional provider-specific metadata.

        Returns:
            A PaymentResult; currently always returns failure.
        """
        # TODO: Implement real Stripe charge
        logger.warning("StripePaymentGateway.charge() is a placeholder")
        return PaymentResult(
            success=False,
            error_message="Stripe integration not yet implemented.",
        )

    async def check_status(self, payment_id: str) -> PaymentStatus:
        """Check payment status via Stripe (not yet implemented).

        Args:
            payment_id: The Stripe payment intent ID.

        Returns:
            Always PENDING as placeholder.
        """
        # TODO: Implement real Stripe status check
        logger.warning("StripePaymentGateway.check_status() is a placeholder")
        return PaymentStatus.PENDING
