import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jose import jwt, jwk

from backend_common.exceptions import NotAuthenticatedException

ALGORITHM = "RS256"
KID = "test-key-id"
ISSUER = "http://localhost:8080/realms/tskhra"

_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_public_key = _private_key.public_key()

_public_jwk = jwk.RSAKey(algorithm=ALGORITHM, key=_public_key.public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo,
).decode()).to_dict()
_public_jwk["kid"] = KID

JWKS = {"keys": [_public_jwk]}


def _make_token(claims: dict) -> str:
    return jwt.encode(
        claims,
        _private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode(),
        algorithm=ALGORITHM,
        headers={"kid": KID},
    )


@pytest.fixture(autouse=True)
def _mock_jwks():
    with patch("backend_common.auth._jwks_cache", JWKS):
        yield


@pytest.mark.asyncio
async def test_get_current_user_id_valid():
    from src.app.infra.auth.auth import get_current_user_id

    user_id = str(uuid4())
    token = _make_token({"sub": user_id, "iss": ISSUER})

    result = await get_current_user_id(token)
    assert str(result) == user_id


@pytest.mark.asyncio
async def test_get_current_user_id_invalid_token():
    from src.app.infra.auth.auth import get_current_user_id

    with pytest.raises(NotAuthenticatedException):
        await get_current_user_id("invalid.token.here")


@pytest.mark.asyncio
async def test_get_current_user_id_no_sub():
    from src.app.infra.auth.auth import get_current_user_id

    token = _make_token({"iss": ISSUER})

    with pytest.raises(NotAuthenticatedException):
        await get_current_user_id(token)
