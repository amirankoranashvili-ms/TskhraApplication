import logging
from uuid import UUID

import httpx
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from jose import jwt, JWTError, jwk
from jose.utils import base64url_decode

from backend_common.exceptions import NotAuthenticatedException

logger = logging.getLogger(__name__)

_jwks_cache: dict | None = None


async def _fetch_jwks(jwks_uri: str) -> dict:
    global _jwks_cache
    if _jwks_cache:
        return _jwks_cache
    async with httpx.AsyncClient() as client:
        resp = await client.get(jwks_uri)
        resp.raise_for_status()
        _jwks_cache = resp.json()
    return _jwks_cache


def _get_signing_key(token: str, jwks: dict) -> dict:
    headers = jwt.get_unverified_headers(token)
    kid = headers.get("kid")
    for key in jwks.get("keys", []):
        if key["kid"] == kid:
            return key
    raise NotAuthenticatedException("Signing key not found")


def create_keycloak_validator(
    keycloak_url: str,
    realm: str,
    *,
    audience: str | None = None,
):
    base = f"{keycloak_url}/realms/{realm}"
    jwks_uri = f"{base}/protocol/openid-connect/certs"
    issuer = base

    bearer_scheme = HTTPBearer()

    async def get_current_user_id(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    ) -> UUID:
        token = credentials.credentials
        try:
            jwks = await _fetch_jwks(jwks_uri)
            signing_key = _get_signing_key(token, jwks)

            options = {"verify_aud": False}
            if audience:
                options = {"verify_aud": True}

            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=audience,
                options={**options, "verify_iss": False},
            )

            user_id = payload.get("sub")
            if not user_id:
                raise NotAuthenticatedException("Missing sub claim")

            return UUID(user_id)
        except JWTError as e:
            logger.warning("JWT validation failed: %s", e)
            raise NotAuthenticatedException("Invalid token")
        except Exception as e:
            logger.warning("Auth error: %s", e)
            raise NotAuthenticatedException("Authentication failed")

    return bearer_scheme, get_current_user_id


def create_jwt_validator(secret_key: str, token_url: str):
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)

    async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            if user_id is None or token_type != "access":
                raise NotAuthenticatedException()
            return UUID(user_id)
        except JWTError:
            raise NotAuthenticatedException("Invalid token")

    return oauth2_scheme, get_current_user_id
