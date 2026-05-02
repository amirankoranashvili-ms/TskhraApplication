"""Validation functions for seller registration fields.

Provides reusable validators for names, emails, identification numbers,
IBANs, and legal addresses used in seller registration.
"""

import re

NAME_REGEX = r"^[a-zA-Zა-ჰ]+$"
IBAN_LENGTH = 22
IBAN_COUNTRY_CODE = "GE"
ID_NUMBER_LENGTH = (11, 9)


def validate_and_format_name(v: str) -> str:
    """Validate that a name contains only letters and title-case it.

    Args:
        v: The name string to validate.

    Returns:
        The title-cased name.

    Raises:
        ValueError: If the name contains non-letter characters.
    """
    if not re.match(NAME_REGEX, v):
        raise ValueError("Name must contain only letters.")
    return v.title()


def lower_case_email(v: str) -> str:
    """Convert an email address to lowercase.

    Args:
        v: The email string.

    Returns:
        The lowercased email string.
    """
    return v.lower()


def validate_identification_number(v: str) -> str:
    """Validate that an identification number has the correct length.

    Args:
        v: The identification number string.

    Returns:
        The validated identification number.

    Raises:
        ValueError: If the length is not 9 or 11 characters.
    """
    if len(v) not in ID_NUMBER_LENGTH:
        raise ValueError("Identification number must be either 9 or 11 digits long")
    return v


def validate_iban(v: str) -> str:
    """Validate and normalize a Georgian IBAN.

    Args:
        v: The IBAN string to validate.

    Returns:
        The uppercased and stripped IBAN.

    Raises:
        ValueError: If the IBAN length or country code is invalid.
    """
    v = v.strip().upper()
    if len(v) != IBAN_LENGTH:
        raise ValueError(f"IBAN must be exactly {IBAN_LENGTH} characters long")
    if not v.startswith(IBAN_COUNTRY_CODE):
        raise ValueError(f"IBAN country code must be {IBAN_COUNTRY_CODE}")
    return v


def validate_legal_address(v: str) -> str:
    """Validate and strip a legal address.

    Args:
        v: The address string to validate.

    Returns:
        The stripped address string.

    Raises:
        ValueError: If the address is shorter than 5 characters.
    """
    v = v.strip()
    if len(v) < 5:
        raise ValueError("Legal address must be at least 5 characters long")
    return v
