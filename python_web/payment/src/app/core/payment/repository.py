"""Abstract repository interface for payment persistence."""

from typing import Protocol
from uuid import UUID

from src.app.core.payment.entities import Payment, PaymentStatus


class IPaymentRepository(Protocol):
    """Protocol defining the contract for payment data access."""

    async def create(self, payment: Payment) -> Payment:
        """Persist a new payment record.

        Args:
            payment: The payment entity to store.

        Returns:
            The persisted payment with any generated fields populated.
        """
        ...

    async def get_by_order_id(self, order_id: UUID) -> Payment | None:
        """Retrieve a payment by its associated order ID.

        Args:
            order_id: The UUID of the order.

        Returns:
            The Payment if found, otherwise None.
        """
        ...

    async def get_by_provider_id(self, provider_payment_id: str) -> Payment | None:
        """Retrieve a payment by its external provider ID.

        Args:
            provider_payment_id: The payment ID from the payment provider.

        Returns:
            The Payment if found, otherwise None.
        """
        ...

    async def update_status(
        self,
        payment_id: UUID,
        status: PaymentStatus,
        provider_payment_id: str | None = None,
    ) -> Payment | None:
        """Update the status of an existing payment.

        Args:
            payment_id: The UUID of the payment to update.
            status: The new payment status.
            provider_payment_id: Optional provider ID to associate.

        Returns:
            The updated Payment if found, otherwise None.
        """
        ...
