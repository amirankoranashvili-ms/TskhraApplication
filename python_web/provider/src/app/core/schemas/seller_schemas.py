"""Request and response schemas for seller profile operations.

Defines Pydantic models for seller registration input and
seller listing output.
"""

from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.app.core.sellers.entities import PlatformSeller
from src.app.core.sellers.types import (
    GeorgianIban,
    IdentificationNumber,
    LegalAddress,
    LowerCaseEmail,
    PersonNameStr,
)


class PlatformSellerCreate(BaseModel):
    """Request schema for creating a new seller profile.

    Attributes:
        identification_number: Business identification number.
        name: Legal name of the seller.
        legal_address: Registered legal address.
        contact_phone: Contact phone number.
        contact_email: Contact email address.
        bank_account_number: Georgian IBAN for payouts.
    """

    identification_number: IdentificationNumber
    name: PersonNameStr
    legal_address: LegalAddress
    contact_phone: PhoneNumber
    contact_email: LowerCaseEmail
    bank_account_number: GeorgianIban


class PlatformSellersResponse(BaseModel):
    """Response schema for listing seller profiles.

    Attributes:
        sellers: List of seller profile entities.
    """

    sellers: list[PlatformSeller]
