"""Port interface for IBAN account number validation.

Defines the protocol for external IBAN validation services.
"""

from typing import Protocol


class IIbanValidator(Protocol):
    """Protocol for IBAN validation implementations."""

    async def validate(self, account_number: str) -> None:
        """Validate an IBAN account number.

        Args:
            account_number: The IBAN string to validate.

        Raises:
            InvalidIbanException: If the IBAN is invalid.
            IbanValidationUnavailableException: If the validation service is unavailable.
        """
        ...
