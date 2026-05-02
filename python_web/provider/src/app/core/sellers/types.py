"""Custom annotated types for seller field validation.

Defines reusable Pydantic-compatible type aliases with built-in validation
for seller-specific fields such as names, emails, IBANs, and addresses.
"""

from typing import Annotated

from pydantic import AfterValidator, EmailStr, StringConstraints

from src.app.core.sellers.validators import (
    lower_case_email,
    validate_and_format_name,
    validate_iban,
    validate_identification_number,
    validate_legal_address,
)

LowerCaseEmail = Annotated[EmailStr, AfterValidator(lower_case_email)]

PersonNameStr = Annotated[
    str,
    StringConstraints(min_length=2, max_length=60, strip_whitespace=True),
    AfterValidator(validate_and_format_name),
]

IdentificationNumber = Annotated[str, AfterValidator(validate_identification_number)]

GeorgianIban = Annotated[
    str,
    StringConstraints(min_length=22, max_length=22, strip_whitespace=True),
    AfterValidator(validate_iban),
]

LegalAddress = Annotated[
    str,
    StringConstraints(min_length=5, max_length=255, strip_whitespace=True),
    AfterValidator(validate_legal_address),
]
