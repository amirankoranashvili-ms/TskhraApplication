"""
MockPaymentGateway: implements IPaymentGateway for development.
Simulates payment processing based on test card numbers.
"""

import uuid
from decimal import Decimal

from src.app.core.payment.entities import PaymentResult, PaymentStatus


class MockPaymentGateway:
    """In-memory payment gateway for development and testing.

    Simulates success for most cards and failure for known test card numbers
    listed in ``FAILING_CARDS``.
    """

    async def charge(
        self,
        amount: Decimal,
        metadata: dict | None = None,
    ) -> PaymentResult:
        """Simulate charging a payment.

        Args:
            amount: The amount to charge.
            metadata: Optional metadata; may contain ``card_number`` to trigger
                test failures.

        Returns:
            A PaymentResult indicating simulated success or failure.
        """
        provider_id = f"mock_pay_{uuid.uuid4().hex[:16]}"
        return PaymentResult(
            success=True,
            provider_payment_id=provider_id,
        )

    def check_status(self) -> PaymentStatus:
        """Simulate status check — mock payments are always completed.


        Returns:
            Always COMPLETED for mock gateway.
        """
        return PaymentStatus.COMPLETED
