"""KeepZ payment gateway implementation with AES-256-CBC + RSA-OAEP hybrid encryption."""

import base64
import json
import logging
import os
import uuid
from decimal import Decimal
from typing import Any

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from src.app.core.payment.entities import PaymentResult, PaymentStatus

logger = logging.getLogger(__name__)


class KeepZPaymentGateway:
    """KeepZ payment gateway using AES-256-CBC + RSA-OAEP hybrid encryption."""

    def __init__(
        self,
        identifier: str,
        integrator_id: str,
        receiver_id: str,
        receiver_type: str,
        rsa_public_key: str,
        rsa_private_key: str,
        base_url: str = "https://gateway.keepz.me/ecommerce-service",
        callback_url: str = "",
    ) -> None:
        self.identifier = identifier
        self.integrator_id = integrator_id
        self.receiver_id = receiver_id
        self.receiver_type = receiver_type
        self._rsa_public_key = rsa_public_key
        self._rsa_private_key = rsa_private_key
        self.base_url = base_url
        self.callback_url = callback_url

    def _encrypt_rsa(self, data: str) -> str:
        pem = f"-----BEGIN PUBLIC KEY-----\n{self._rsa_public_key}\n-----END PUBLIC KEY-----"
        public_key = serialization.load_pem_public_key(pem.encode("utf-8"))
        encrypted = public_key.encrypt(
            data.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return base64.b64encode(encrypted).decode("utf-8")

    def _decrypt_rsa(self, data: str) -> str:
        pem = f"-----BEGIN PRIVATE KEY-----\n{self._rsa_private_key}\n-----END PRIVATE KEY-----"
        private_key = serialization.load_pem_private_key(
            pem.encode("utf-8"), password=None
        )
        decrypted = private_key.decrypt(
            base64.b64decode(data),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return decrypted.decode("utf-8")

    def _encrypt_payload(self, payload: dict) -> tuple[str, str]:
        aes_key = os.urandom(32)
        iv = os.urandom(16)

        data = json.dumps(payload)
        pad_len = 16 - len(data) % 16
        padded_data = data + chr(pad_len) * pad_len

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        encrypted_bytes = (
            encryptor.update(padded_data.encode("utf-8")) + encryptor.finalize()
        )
        encrypted_data = base64.b64encode(encrypted_bytes).decode("utf-8")

        aes_properties = (
            base64.b64encode(aes_key).decode("utf-8")
            + "."
            + base64.b64encode(iv).decode("utf-8")
        )
        encrypted_keys = self._encrypt_rsa(aes_properties)

        return encrypted_data, encrypted_keys

    def _decrypt_response(self, encrypted_data: str, encrypted_keys: str) -> dict:
        decrypted_props = self._decrypt_rsa(encrypted_keys)
        key_b64, iv_b64 = decrypted_props.split(".")
        aes_key = base64.b64decode(key_b64)
        iv = base64.b64decode(iv_b64)

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted_padded = (
            decryptor.update(base64.b64decode(encrypted_data)) + decryptor.finalize()
        )

        pad_length = decrypted_padded[-1]
        decrypted_data = decrypted_padded[:-pad_length]
        return json.loads(decrypted_data)

    def _build_request_body(self, payload: dict) -> dict:
        encrypted_data, encrypted_keys = self._encrypt_payload(payload)
        return {
            "identifier": self.identifier,
            "encryptedData": encrypted_data,
            "encryptedKeys": encrypted_keys,
            "aes": True,
        }

    async def charge(
        self,
        amount: Decimal,
        metadata: dict[str, Any] | None = None,
    ) -> PaymentResult:
        metadata = metadata or {}
        integrator_order_id = (
            metadata.get("payment_id") or metadata.get("order_id") or str(uuid.uuid4())
        )

        payload = {
            "amount": float(amount),
            "receiverId": self.receiver_id,
            "receiverType": self.receiver_type,
            "integratorId": self.integrator_id,
            "integratorOrderId": integrator_order_id,
            "currency": metadata.get("currency", "GEL"),
        }
        if metadata.get("successRedirectUri"):
            payload["successRedirectUri"] = metadata["successRedirectUri"]
        if metadata.get("failRedirectUri"):
            payload["failRedirectUri"] = metadata["failRedirectUri"]
        if self.callback_url:
            payload["callbackUri"] = self.callback_url

        body = self._build_request_body(payload)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/integrator/order", json=body
                )
        except httpx.RequestError as exc:
            logger.error("KeepZ charge request error: %s", exc)
            return PaymentResult(success=False, error_message=f"Network error: {exc}")

        if response.status_code not in (200, 201):
            error = response.json()
            logger.error(
                "KeepZ charge failed: status=%s body=%s", response.status_code, error
            )
            return PaymentResult(
                success=False,
                error_message=error.get("message", "KeepZ order creation failed"),
            )

        resp = response.json()
        decrypted = self._decrypt_response(resp["encryptedData"], resp["encryptedKeys"])
        return PaymentResult(
            success=True,
            provider_payment_id=decrypted.get("integratorOrderId"),
            redirect_url=decrypted.get("urlForQR"),
            requires_redirect=True,
        )

    async def check_status(self, payment_id: str) -> PaymentStatus:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/integrator/order/status",
                    params={
                        "integratorId": self.integrator_id,
                        "integratorOrderId": payment_id,
                        "identifier": self.identifier,
                    },
                )
        except httpx.RequestError as exc:
            logger.error("KeepZ status check request error: %s", exc)
            return PaymentStatus.PENDING

        if response.status_code not in (200, 201):
            logger.error(
                "KeepZ status check failed: status=%s body=%s",
                response.status_code,
                response.text,
            )
            return PaymentStatus.PENDING

        resp = response.json()
        # KeepZ may return plain JSON or encrypted response
        if "encryptedData" in resp:
            data = self._decrypt_response(resp["encryptedData"], resp["encryptedKeys"])
        else:
            data = resp

        keepz_status = str(data.get("orderStatus") or data.get("status") or "").upper()
        if keepz_status in ("PAID", "SUCCESS", "COMPLETED", "FINISHED"):
            return PaymentStatus.COMPLETED
        if keepz_status in ("FAILED", "CANCELLED", "DECLINED", "REJECTED"):
            return PaymentStatus.FAILED
        return PaymentStatus.PENDING
