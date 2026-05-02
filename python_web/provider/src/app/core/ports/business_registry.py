"""Port interface for business registry validation.

Defines the protocol for external business registry lookup services.
"""

from typing import Protocol


class IBusinessRegistryValidator(Protocol):
    """Protocol for business registry validation implementations."""

    async def validate(self, identification_number: str) -> None:
        """Validate a business identification number against the registry.

        Args:
            identification_number: The business ID to validate.

        Raises:
            InvalidIdentificationNumberException: If the ID is not found.
            IdentificationValidationUnavailableException: If the service is unavailable.
        """
        ...
