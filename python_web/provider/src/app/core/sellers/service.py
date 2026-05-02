"""Service layer for seller profile retrieval operations."""

import logging
from uuid import UUID

from src.app.core.sellers.entities import PlatformSeller
from src.app.core.sellers.exceptions import SellerNotFoundException
from src.app.core.sellers.repository import ISellerRepository

logger = logging.getLogger(__name__)


class SellerService:
    """Service for querying seller profiles.

    Provides read-only access to seller data with ownership verification.
    """

    def __init__(self, repository: ISellerRepository) -> None:
        """Initialize the seller service.

        Args:
            repository: Seller repository implementation.
        """
        self.repository = repository

    async def get_seller_profiles(self, user_id: UUID) -> list[PlatformSeller]:
        """Retrieve all seller profiles belonging to a user.

        Args:
            user_id: UUID of the authenticated user.

        Returns:
            List of seller profiles owned by the user.
        """
        return await self.repository.get_by_user_id(user_id)

    async def get_seller_profile(
        self, user_id: UUID, supplier_id: int
    ) -> PlatformSeller:
        """Retrieve a specific seller profile with ownership check.

        Args:
            user_id: UUID of the authenticated user.
            supplier_id: ID of the seller profile to retrieve.

        Returns:
            The matching seller profile.

        Raises:
            SellerNotFoundException: If the profile does not exist or
                does not belong to the user.
        """
        seller = await self.repository.get_by_supplier_id(supplier_id)
        if not seller or seller.user_id != user_id:
            raise SellerNotFoundException()
        return seller
