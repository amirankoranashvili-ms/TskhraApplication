import pytest


async def test_webhook_payment_succeeded(client, seed_order, seed_payment):
    ac, _ = client
    resp = await ac.post(
        "/webhooks/payment",
        json={
            "integratorOrderId": "test_order_abc123",
            "status": "SUCCESS",
        },
    )
    assert resp.status_code == 200
    assert "processed" in resp.json()["message"].lower()


async def test_webhook_payment_failed(client, seed_order, seed_payment):
    ac, _ = client
    resp = await ac.post(
        "/webhooks/payment",
        json={
            "integratorOrderId": "test_order_abc123",
            "status": "FAILED",
        },
    )
    assert resp.status_code == 200
    assert "processed" in resp.json()["message"].lower()


async def test_webhook_unknown_status(client, seed_order, seed_payment):
    ac, _ = client
    resp = await ac.post(
        "/webhooks/payment",
        json={
            "integratorOrderId": "test_order_abc123",
            "status": "PENDING",
        },
    )
    assert resp.status_code == 200
    assert "unknown" in resp.json()["message"].lower()


async def test_webhook_payment_not_found(client):
    ac, _ = client
    resp = await ac.post(
        "/webhooks/payment",
        json={
            "integratorOrderId": "nonexistent_xyz",
            "status": "SUCCESS",
        },
    )
    assert resp.status_code == 200
    assert "not found" in resp.json()["message"].lower()


async def test_webhook_invalid_payload(client):
    ac, _ = client
    resp = await ac.post("/webhooks/payment", json={"status": "SUCCESS"})
    assert resp.status_code == 200
    assert "parse error" in resp.json()["message"].lower()
