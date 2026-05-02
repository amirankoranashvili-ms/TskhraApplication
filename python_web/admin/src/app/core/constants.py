"""Constants and enumerations for the admin service."""

from enum import Enum


class SessionKeys:
    """Keys used to store values in the user session."""

    AUTHENTICATED = "authenticated"
    USERNAME = "username"


class VerificationStatus(str, Enum):
    """Possible statuses for a verification request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class VerificationRequestType(str, Enum):
    """Types of entities that can be submitted for verification."""

    PRODUCT = "product"
    SELLER = "seller"


class VendorStatus(str, Enum):
    """Possible statuses for a vendor seller."""

    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    PENDING = "PENDING"
