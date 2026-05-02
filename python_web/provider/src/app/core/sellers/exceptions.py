"""Exception classes for seller domain operations.

Each exception maps to a specific error scenario in the seller registration
and management workflow.
"""

from backend_common.exceptions import (
    BaseAppException,
    ConflictException,
    EntityNotFoundException,
    ValidationException,
)


class SellerAlreadyExistsException(ConflictException):
    """Raised when attempting to register a seller that already exists."""

    error_code = "SELLER_ALREADY_EXISTS"
    message = "Seller already exists."


class SellerRegistrationPendingException(ConflictException):
    """Raised when a seller registration is already pending approval."""

    error_code = "SELLER_REGISTRATION_PENDING"
    message = "Seller registration is pending admin approval."


class SellerDataUnchangedException(ValidationException):
    """Raised when reapplying with identical data after rejection."""

    error_code = "SELLER_DATA_UNCHANGED"
    message = "Please submit different data to reapply."


class IdentificationNumberAlreadyRegisteredException(ConflictException):
    """Raised when the identification number belongs to another seller."""

    error_code = "ID_NUMBER_ALREADY_REGISTERED"
    message = "A seller with this identification number is already registered."


class SellerNotFoundException(EntityNotFoundException):
    """Raised when a seller profile cannot be found."""

    error_code = "SELLER_NOT_FOUND"
    message = "Seller profile not found."


class InvalidIbanException(ValidationException):
    """Raised when IBAN validation fails."""

    error_code = "INVALID_IBAN"
    message = "Invalid IBAN account number."


class IbanValidationUnavailableException(BaseAppException):
    """Raised when the IBAN validation service is unreachable."""

    error_code = "IBAN_VALIDATION_UNAVAILABLE"
    message = "IBAN validation service is temporarily unavailable."


class InvalidIdentificationNumberException(ValidationException):
    """Raised when the identification number is not found in the registry."""

    error_code = "INVALID_ID_NUMBER"
    message = "Identification number not found in the business registry."


class IdentificationValidationUnavailableException(BaseAppException):
    """Raised when the business registry service is unreachable."""

    error_code = "ID_VALIDATION_UNAVAILABLE"
    message = "Business registry validation service is temporarily unavailable."
