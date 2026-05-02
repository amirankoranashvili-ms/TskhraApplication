"""Reusable annotated Pydantic field types for common domain values.

Defines constrained type aliases for emails and passwords that can be
used directly in Pydantic models across all services.
"""

from typing import Annotated

from pydantic import EmailStr, Field


LowerCaseEmail = Annotated[EmailStr, Field(description="Lowercase email address")]

PasswordStr = Annotated[
    str,
    Field(min_length=8, max_length=128, description="User password"),
]