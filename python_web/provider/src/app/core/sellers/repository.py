"""Abstract repository interface for seller persistence.

Defines the protocol that all seller repository implementations must follow.
"""

from typing import Protocol
from uuid import UUID

from src.app.core.sellers.entities import PlatformSeller


class ISellerRepository(Protocol):
    """Repository protocol for managing seller profiles.

    Implementations must provide async methods for CRUD operations
    on seller data.
    """

    async def create(self, seller_data: PlatformSeller) -> PlatformSeller:
        """Create a new seller profile.

        Args:
            seller_data: Seller entity with registration data.

        Returns:
            The created seller with assigned supplier_id.
        """
        pass

    async def get_by_user_id(self, user_id: UUID) -> list[PlatformSeller]:
        """Get all seller profiles for a user.

        Args:
            user_id: UUID of the owning user.

        Returns:
            List of seller profiles.
        """
        pass

    async def get_by_user_id_any_status(self, user_id: UUID) -> PlatformSeller | None:
        """Get seller profile by user ID regardless of status.

        Args:
            user_id: UUID of the owning user.

        Returns:
            The seller profile, or None if not found.
        """
        pass

    async def update(
        self, supplier_id: int, seller_data: PlatformSeller
    ) -> PlatformSeller:
        """Update an existing seller profile.

        Args:
            supplier_id: ID of the seller to update.
            seller_data: Updated seller entity data.

        Returns:
            The updated seller profile.
        """
        pass

    async def get_by_identification_number(
        self, identification_number: str
    ) -> PlatformSeller | None:
        """Get seller profile by identification number.

        Args:
            identification_number: Business or personal ID number.

        Returns:
            The matching seller profile, or None if not found.
        """
        pass

    async def get_by_supplier_id(self, supplier_id: int) -> PlatformSeller | None:
        """Get active seller profile by supplier ID.

        Args:
            supplier_id: The supplier identifier.

        Returns:
            The matching active seller profile, or None if not found.
        """
        pass
