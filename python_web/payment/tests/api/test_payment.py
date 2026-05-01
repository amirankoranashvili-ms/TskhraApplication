from uuid import uuid4

import pytest

from src.app.infra.database.models import OrderDB, OrderItemDB
from tests.conftest import TEST_USER_ID


async def test_get_order_history_empty(client):
    ac, _ = client
    resp = await ac.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1


async def test_get_order_history_with_orders(client, seed_order):
    ac, _ = client
    resp = await ac.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == str(seed_order.id)


async def test_get_order_history_pagination(client, db_session):
    for _ in range(3):
        order = OrderDB(
            id=uuid4(), user_id=TEST_USER_ID, status="PENDING", total_amount=10.0
        )
        db_session.add(order)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get("/?page=1&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["total_pages"] == 2


async def test_get_order_details(client, seed_order):
    ac, _ = client
    resp = await ac.get(f"/{seed_order.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(seed_order.id)
    assert data["total_amount"] == 99.99
    assert len(data["items"]) == 1
    assert data["items"][0]["entity_id"] == "product-123"


async def test_get_order_details_not_found(client):
    ac, _ = client
    resp = await ac.get(f"/{uuid4()}")
    assert resp.status_code == 404


async def test_get_order_details_wrong_user(client, db_session):
    other_order = OrderDB(
        id=uuid4(), user_id=uuid4(), status="PENDING", total_amount=50.0
    )
    db_session.add(other_order)
    await db_session.commit()

    ac, _ = client
    resp = await ac.get(f"/{other_order.id}")
    assert resp.status_code == 403


async def test_process_payment_success(client, seed_order):
    ac, _ = client
    resp = await ac.post(f"/{seed_order.id}/pay")
    assert resp.status_code == 200
    data = resp.json()
    assert data["payment"] is not None
    assert data["payment"]["status"] == "PENDING"
    assert data["payment"]["redirect_url"] == "https://pay.keepz.me/test"
    assert data["payment"]["provider_payment_id"] == "test_order_abc123"


async def test_process_payment_returns_existing_pending(
    client, seed_order, seed_payment
):
    ac, _ = client
    resp = await ac.post(f"/{seed_order.id}/pay")
    assert resp.status_code == 200
    data = resp.json()
    assert data["payment"]["redirect_url"] == "https://pay.keepz.me/test"


async def test_process_payment_order_not_found(client):
    ac, _ = client
    resp = await ac.post(f"/{uuid4()}/pay")
    assert resp.status_code == 404


async def test_process_payment_wrong_user(client, db_session):
    other_order = OrderDB(
        id=uuid4(), user_id=uuid4(), status="PENDING", total_amount=50.0
    )
    db_session.add(other_order)
    await db_session.commit()

    ac, _ = client
    resp = await ac.post(f"/{other_order.id}/pay")
    assert resp.status_code == 403


async def test_process_payment_with_redirect_uris(client, seed_order):
    ac, _ = client
    resp = await ac.post(
        f"/{seed_order.id}/pay",
        params={
            "success_redirect_uri": "https://example.com/success",
            "fail_redirect_uri": "https://example.com/fail",
        },
    )
    assert resp.status_code == 400


async def test_process_payment_invalid_redirect_uri(client, seed_order, monkeypatch):
    from src.app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "ALLOWED_REDIRECT_ORIGINS", "https://allowed.com")

    ac, _ = client
    resp = await ac.post(
        f"/{seed_order.id}/pay",
        params={"success_redirect_uri": "https://evil.com/steal"},
    )
    assert resp.status_code == 400


async def test_verify_payment_completed(client, seed_order, seed_payment):
    ac, _ = client
    resp = await ac.post(f"/{seed_order.id}/verify")
    assert resp.status_code == 200
    data = resp.json()
    assert data["payment"]["status"] == "COMPLETED"


async def test_verify_payment_order_not_found(client):
    ac, _ = client
    resp = await ac.post(f"/{uuid4()}/verify")
    assert resp.status_code == 404


async def test_verify_payment_no_payment_yet(client, seed_order):
    ac, _ = client
    resp = await ac.post(f"/{seed_order.id}/verify")
    assert resp.status_code == 404
