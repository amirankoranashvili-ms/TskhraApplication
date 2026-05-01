"""Interactor for seller registration use case.

Handles new seller registration, rejected seller reapplication,
and publishes domain events upon success.
"""

import logging

from src.app.core.ports.business_registry import IBusinessRegistryValidator
from src.app.core.ports.event_publisher import IEventPublisher
from src.app.core.ports.iban_validator import IIbanValidator
from src.app.core.sellers.entities import PlatformSeller, SellerStatus
from src.app.core.sellers.exceptions import (
    IdentificationNumberAlreadyRegisteredException,
    SellerAlreadyExistsException,
    SellerDataUnchangedException,
    SellerRegistrationPendingException,
)
from src.app.core.sellers.repository import ISellerRepository

logger = logging.getLogger(__name__)


class RegisterSellerInteractor:
    """Orchestrates seller registration with validation and event publishing.

    Validates the seller's IBAN and business registration, checks for
    duplicate registrations, and handles reapplication for rejected sellers.
    """

    def __init__(
        self,
        repository: ISellerRepository,
        publisher: IEventPublisher,
        iban_validator: IIbanValidator,
        registry_validator: IBusinessRegistryValidator,
    ) -> None:
        """Initialize the interactor with its dependencies.

        Args:
            repository: Seller persistence repository.
            publisher: Event publisher for domain events.
            iban_validator: IBAN validation port.
            registry_validator: Business registry validation port.
        """
        self.repository = repository
        self.publisher = publisher
        self.iban_validator = iban_validator
        self.registry_validator = registry_validator

    async def execute(self, seller_data: PlatformSeller) -> PlatformSeller:
        """Execute the seller registration use case.

        Args:
            seller_data: Seller entity with registration data.

        Returns:
            The created or updated seller profile.

        Raises:
            IdentificationNumberAlreadyRegisteredException: If the ID number
                belongs to another user.
            SellerRegistrationPendingException: If a pending registration exists.
            SellerAlreadyExistsException: If an active seller already exists.
            SellerDataUnchangedException: If reapplying with unchanged data.
        """
        await self.registry_validator.validate(seller_data.identification_number)
        await self.iban_validator.validate(seller_data.bank_account_number)

        existing_by_id = await self.repository.get_by_identification_number(
            seller_data.identification_number
        )
        if existing_by_id and existing_by_id.user_id != seller_data.user_id:
            raise IdentificationNumberAlreadyRegisteredException()

        existing_seller = await self.repository.get_by_user_id_any_status(
            seller_data.user_id
        )
        if existing_seller:
            if existing_seller.status == SellerStatus.Pending:
                raise SellerRegistrationPendingException()
            if existing_seller.status == SellerStatus.Active:
                raise SellerAlreadyExistsException()
            if existing_seller.status == SellerStatus.Rejected:
                if not self._has_data_changed(existing_seller, seller_data):
                    raise SellerDataUnchangedException()
                updated = await self.repository.update(
                    existing_seller.supplier_id, seller_data
                )
                await self._publish_seller_event(updated, "updated")
                return updated

        created = await self.repository.create(seller_data)
        await self._publish_seller_event(created, "created")
        return created

    @staticmethod
    def _has_data_changed(existing: PlatformSeller, new: PlatformSeller) -> bool:
        """Check whether the seller data has changed from the existing record.

        Args:
            existing: The current seller profile.
            new: The incoming seller data.

        Returns:
            True if any tracked field differs between existing and new.
        """
        fields = (
            "name",
            "identification_number",
            "legal_address",
            "contact_phone",
            "contact_email",
            "bank_account_number",
        )
        return any(getattr(existing, f) != getattr(new, f) for f in fields)

    async def _publish_seller_event(self, seller: PlatformSeller, event: str) -> None:
        """Publish a seller domain event to the message broker.

        Args:
            seller: The seller entity to include in the event payload.
            event: Event type, either "created" or "updated".
        """
        payload = {
            "supplier_id": seller.supplier_id,
            "name": seller.name,
            "user_id": str(seller.user_id),
            "identification_number": seller.identification_number,
            "legal_address": seller.legal_address,
            "contact_phone": seller.contact_phone,
            "contact_email": seller.contact_email,
            "bank_account_number": seller.bank_account_number,
        }
        if event == "created":
            await self.publisher.publish_seller_created(payload)
        elif event == "updated":
            await self.publisher.publish_seller_updated(payload)
        logger.info(
            "Published seller.%s event for supplier_id=%s", event, seller.supplier_id
        )
