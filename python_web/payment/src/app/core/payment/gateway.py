"""Abstract gateway interface for payment provider integrations."""

from decimal import Decimal
from typing import Any, Protocol

from src.app.core.payment.entities import PaymentResult, PaymentStatus


class IPaymentGateway(Protocol):
    """Protocol defining the contract for payment provider operations."""

    async def charge(
        self,
        amount: Decimal,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentResult:
        """Charge the given amount using the specified payment method.

        Args:
            amount: The amount to charge.
            metadata: Optional provider-specific metadata.

        Returns:
            A PaymentResult indicating success or failure.
        """
        ...

    async def check_status(self, payment_id: str) -> PaymentStatus:
        """Check the current status of a payment at the provider.

        Args:
            payment_id: The provider's payment identifier.

        Returns:
            The current PaymentStatus.
        """
        ...
