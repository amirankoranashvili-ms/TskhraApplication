"""Business registry validator using the Georgian Reestri API.

Validates business identification numbers against the Georgian national
business registry (reestri.gov.ge).
"""

import logging

import httpx

from src.app.core.sellers.exceptions import (
    IdentificationValidationUnavailableException,
    InvalidIdentificationNumberException,
)

logger = logging.getLogger(__name__)

NOT_FOUND_MARKER = "ჩანაწერები არ მოიძებნა"


class StubBusinessRegistryValidator:
    """No-op business registry validator that always passes (no external HTTP call)."""

    async def validate(self, identification_number: str) -> None:
        pass


class ReestriBusinessValidator:
    """Validates business IDs against the Georgian national business registry."""

    URL = "https://enreg.reestri.gov.ge/_dea/main.php"

    def __init__(self, http_client: httpx.AsyncClient) -> None:
        """Initialize with an httpx async client.

        Args:
            http_client: Configured httpx AsyncClient.
        """
        self._http_client = http_client

    async def validate(self, identification_number: str) -> None:
        """Validate a business identification number against the registry.

        Args:
            identification_number: The business ID to look up.

        Raises:
            IdentificationValidationUnavailableException: If the API is unreachable.
            InvalidIdentificationNumberException: If the ID is not found.
        """
        try:
            response = await self._http_client.get(
                self.URL,
                params={
                    "c": "search",
                    "m": "find_legal_persons",
                    "s_legal_person_idnumber": identification_number,
                },
            )
            response.raise_for_status()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error("Business registry validation request failed: %s", e)
            raise IdentificationValidationUnavailableException()
        if NOT_FOUND_MARKER in response.text:
            raise InvalidIdentificationNumberException()
