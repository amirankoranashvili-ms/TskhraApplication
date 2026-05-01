"""JWT authentication utilities for FastAPI services.

Provides a factory for creating OAuth2 token validation dependencies
that extract and verify user identity from access tokens.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from uuid import UUID

from backend_common.exceptions import NotAuthenticatedException

ALGORITHM = "HS256"


def create_jwt_validator(secret_key: str, token_url: str):
    """Create an OAuth2 scheme and a FastAPI dependency for JWT validation.

    Args:
        secret_key: The secret key used to decode JWT tokens.
        token_url: The OAuth2 token endpoint URL for OpenAPI docs.

    Returns:
        A tuple of ``(oauth2_scheme, get_current_user_id)`` where the scheme
        is an ``OAuth2PasswordBearer`` instance and the dependency is an async
        function that extracts the authenticated user's UUID from the token.

    Raises:
        NotAuthenticatedException: When the token is missing, invalid, or
            not an access token.
    """
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)

    async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
        """Extract and return the authenticated user's UUID from a JWT.

        Args:
            token: The Bearer token extracted by the OAuth2 scheme.

        Returns:
            The user's UUID from the token ``sub`` claim.

        Raises:
            NotAuthenticatedException: When the token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            if user_id is None or token_type != "access":
                raise NotAuthenticatedException()
            return UUID(user_id)
        except JWTError:
            raise NotAuthenticatedException("Invalid token")

    return oauth2_scheme, get_current_user_id
