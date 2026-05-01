"""Domain entities for the seller bounded context.

Defines the core seller data model and status enumeration used throughout
the provider service.
"""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

NO_ID = -1


class SellerStatus(str, Enum):
    """Enumeration of possible seller registration statuses."""

    Pending = "PENDING"
    Active = "ACTIVE"
    Rejected = "REJECTED"


class PlatformSeller(BaseModel):
    """Represents a registered seller on the platform.

    Attributes:
        supplier_id: Unique identifier for the seller.
        name: Legal or display name of the seller.
        user_id: UUID of the user account owning this seller profile.
        identification_number: Business or personal identification number.
        legal_address: Registered legal address.
        contact_phone: Contact phone number.
        contact_email: Contact email address.
        bank_account_number: IBAN bank account number for payouts.
        status: Current registration status.
    """

    supplier_id: int
    name: str
    user_id: UUID
    identification_number: str
    legal_address: str
    contact_phone: str
    contact_email: str
    bank_account_number: str
    status: SellerStatus = SellerStatus.Pending

    model_config = ConfigDict(from_attributes=True)
