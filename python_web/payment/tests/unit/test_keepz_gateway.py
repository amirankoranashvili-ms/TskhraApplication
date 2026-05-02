import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from src.app.core.payment.entities import PaymentStatus
from src.app.infra.gateway.keepz_gateway import KeepZPaymentGateway


@pytest.fixture(scope="module")
def rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    pub_pem = public_key.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    priv_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()

    pub_b64 = "\n".join(pub_pem.strip().split("\n")[1:-1])
    priv_b64 = "\n".join(priv_pem.strip().split("\n")[1:-1])
    return pub_b64, priv_b64


@pytest.fixture
def gateway(rsa_keypair):
    pub, priv = rsa_keypair
    return KeepZPaymentGateway(
        identifier="test-id",
        integrator_id="integ-1",
        receiver_id="recv-1",
        receiver_type="BRANCH",
        rsa_public_key=pub,
        rsa_private_key=priv,
    )


def test_encrypt_decrypt_roundtrip(gateway):
    payload = {"amount": 99.99, "currency": "GEL", "orderId": "order-xyz"}
    encrypted_data, encrypted_keys = gateway._encrypt_payload(payload)
    result = gateway._decrypt_response(encrypted_data, encrypted_keys)
    assert result == payload


def test_build_request_body_structure(gateway):
    body = gateway._build_request_body({"amount": 10})
    assert "identifier" in body
    assert body["identifier"] == "test-id"
    assert "encryptedData" in body
    assert "encryptedKeys" in body
    assert body["aes"] is True


@pytest.mark.asyncio
async def test_check_status_completed(gateway):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"orderStatus": "PAID"}

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch(
        "src.app.infra.gateway.keepz_gateway.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await gateway.check_status("order-123")

    assert result == PaymentStatus.COMPLETED


@pytest.mark.asyncio
async def test_check_status_pending_unknown(gateway):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"orderStatus": "PROCESSING"}

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch(
        "src.app.infra.gateway.keepz_gateway.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await gateway.check_status("order-456")

    assert result == PaymentStatus.PENDING


@pytest.mark.asyncio
async def test_check_status_failed(gateway):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"orderStatus": "FAILED"}

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch(
        "src.app.infra.gateway.keepz_gateway.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await gateway.check_status("order-789")

    assert result == PaymentStatus.FAILED


@pytest.mark.asyncio
async def test_check_status_network_error(gateway):
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(
        side_effect=httpx.RequestError("connection refused", request=MagicMock())
    )

    with patch(
        "src.app.infra.gateway.keepz_gateway.httpx.AsyncClient",
        return_value=mock_client,
    ):
        result = await gateway.check_status("order-err")

    assert result == PaymentStatus.PENDING
