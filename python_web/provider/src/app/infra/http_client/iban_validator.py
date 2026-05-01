"""IBAN validator using the National Bank of Georgia API.

Validates bank account numbers by querying the NBG IBAN validation
endpoint.
"""

import logging

import httpx

from src.app.core.sellers.exceptions import (
    IbanValidationUnavailableException,
    InvalidIbanException,
)

logger = logging.getLogger(__name__)


class StubIbanValidator:
    """No-op IBAN validator that always passes (no external HTTP call)."""

    async def validate(self, account_number: str) -> None:
        pass


class NbgIbanValidator:
    """Validates IBAN numbers using the NBG (National Bank of Georgia) API."""

    URL = "https://nbg.gov.ge/gw/api/ct/paymentsystem/iban/validator"

    def __init__(self, http_client: httpx.AsyncClient) -> None:
        """Initialize with an httpx async client.

        Args:
            http_client: Configured httpx AsyncClient.
        """
        self._http_client = http_client

    async def validate(self, account_number: str) -> None:
        """Validate an IBAN account number via the NBG API.

        Args:
            account_number: The IBAN to validate.

        Raises:
            IbanValidationUnavailableException: If the API is unreachable.
            InvalidIbanException: If the IBAN is invalid.
        """
        try:
            response = await self._http_client.get(
                self.URL,
                params={"accountNumber": account_number},
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.error("IBAN validation request failed: %s", e)
            raise IbanValidationUnavailableException()
        if not data.get("isValid"):
            raise InvalidIbanException()
