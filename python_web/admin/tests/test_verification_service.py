"""Unit tests for VerificationService."""

from unittest.mock import AsyncMock

import pytest
from backend_common.exceptions import ConflictException, EntityNotFoundException

from src.app.core.constants import VerificationStatus
from src.app.core.verification_service import VerificationService
from src.app.infra.database.models.products import VerificationRequestDb


@pytest.fixture
def service(products_session, vendor_session):
    return VerificationService(products_session, vendor_session)


# ── list_pending ──────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestListPending:
    async def test_returns_only_pending(self, service, products_session, seed_data):
        products_session.add_all(
            [
                VerificationRequestDb(
                    request_type="product",
                    status="pending",
                    supplier_id=seed_data["supplier"].id,
                ),
                VerificationRequestDb(
                    request_type="product",
                    status="approved",
                    supplier_id=seed_data["supplier"].id,
                ),
            ]
        )
        await products_session.commit()

        result = await service.list_pending()
        assert len(result) == 1
        assert result[0]["status"] == "pending"

    async def test_empty_when_no_pending(self, service):
        result = await service.list_pending()
        assert result == []

    async def test_ordered_by_id_desc(self, service, products_session, seed_data):
        products_session.add_all(
            [
                VerificationRequestDb(
                    request_type="product",
                    status="pending",
                    supplier_id=seed_data["supplier"].id,
                ),
                VerificationRequestDb(
                    request_type="seller",
                    status="pending",
                    supplier_id=seed_data["supplier"].id,
                ),
            ]
        )
        await products_session.commit()

        result = await service.list_pending()
        assert len(result) == 2
        assert result[0]["id"] > result[1]["id"]

    async def test_contains_expected_keys(self, service, pending_product_request):
        result = await service.list_pending()
        expected_keys = {
            "id",
            "request_type",
            "status",
            "supplier_id",
            "product_id",
            "rejection_reason",
            "created_at",
        }
        assert set(result[0].keys()) == expected_keys


# ── get_with_product ──────────────────────────────────────────────────


@pytest.mark.asyncio
class TestGetWithProduct:
    async def test_returns_request_and_product(
        self, service, pending_product_request, seed_data
    ):
        vr, product = await service.get_with_product(pending_product_request.id)
        assert vr is not None
        assert product is not None
        assert product.title == "Test Product"

    async def test_product_is_none_for_seller_request(
        self, service, pending_seller_request
    ):
        vr, product = await service.get_with_product(pending_seller_request.id)
        assert vr is not None
        assert product is None

    async def test_returns_none_for_nonexistent(self, service):
        vr, product = await service.get_with_product(9999)
        assert vr is None
        assert product is None


# ── _get_pending_request ──────────────────────────────────────────────


@pytest.mark.asyncio
class TestGetPendingRequest:
    async def test_raises_not_found(self, service):
        with pytest.raises(EntityNotFoundException):
            await service._get_pending_request(9999)

    async def test_raises_conflict_when_already_resolved(
        self, service, products_session, seed_data
    ):
        vr = VerificationRequestDb(
            request_type="product",
            status="approved",
            supplier_id=seed_data["supplier"].id,
        )
        products_session.add(vr)
        await products_session.commit()

        with pytest.raises(ConflictException):
            await service._get_pending_request(vr.id)

    async def test_returns_pending(self, service, pending_product_request):
        vr = await service._get_pending_request(pending_product_request.id)
        assert vr.status == VerificationStatus.PENDING.value


# ── approve ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestApprove:
    async def test_approve_product_activates_it(
        self, service, pending_product_request, seed_data
    ):
        publisher = AsyncMock()
        service.publisher = publisher

        result = await service.approve(pending_product_request.id, "admin")

        assert result["status"] == "approved"
        await service.products_session.refresh(seed_data["product"])
        assert seed_data["product"].is_active is True

    async def test_approve_product_publishes_event(
        self, service, pending_product_request, seed_data
    ):
        publisher = AsyncMock()
        service.publisher = publisher

        await service.approve(pending_product_request.id, "admin")

        publisher.publish.assert_called_once()
        call_args = publisher.publish.call_args
        assert call_args[0][0] == "product.verified"

    async def test_approve_seller_activates_platform_seller(
        self, service, pending_seller_request, seed_data
    ):
        result = await service.approve(pending_seller_request.id, "admin")

        assert result["status"] == "approved"
        await service.products_session.refresh(seed_data["seller"])
        assert seed_data["seller"].is_active is True

    async def test_approve_seller_updates_vendor_db(
        self, service, pending_seller_request
    ):
        await service.approve(pending_seller_request.id, "admin")

        service.vendor_session.execute.assert_called_once()
        service.vendor_session.commit.assert_called_once()

    async def test_sets_resolved_fields(self, service, pending_product_request):
        await service.approve(pending_product_request.id, "test-admin")

        await service.products_session.refresh(pending_product_request)
        assert pending_product_request.resolved_by_admin_id == "test-admin"
        assert pending_product_request.resolved_at is not None
        assert pending_product_request.status == VerificationStatus.APPROVED.value


# ── reject ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestReject:
    async def test_reject_product_soft_deletes_it(
        self, service, pending_product_request, seed_data
    ):
        publisher = AsyncMock()
        service.publisher = publisher

        result = await service.reject(
            pending_product_request.id, "admin", "Bad quality"
        )

        assert result["status"] == "rejected"
        assert result["reason"] == "Bad quality"
        await service.products_session.refresh(seed_data["product"])
        assert seed_data["product"].is_deleted is True
        assert seed_data["product"].is_active is False

    async def test_reject_product_publishes_event(
        self, service, pending_product_request, seed_data
    ):
        publisher = AsyncMock()
        service.publisher = publisher

        await service.reject(pending_product_request.id, "admin", "Reason")

        publisher.publish.assert_called_once()
        call_args = publisher.publish.call_args
        assert call_args[0][0] == "product.upload.rejected"
        assert call_args[0][1]["error_message"] == "Reason"

    async def test_reject_sets_reason_and_status(
        self, service, pending_product_request
    ):
        await service.reject(pending_product_request.id, "admin", "Not compliant")

        await service.products_session.refresh(pending_product_request)
        assert pending_product_request.rejection_reason == "Not compliant"
        assert pending_product_request.status == VerificationStatus.REJECTED.value
        assert pending_product_request.resolved_at is not None

    async def test_reject_seller_deactivates_platform_seller(
        self, service, pending_seller_request, seed_data
    ):
        await service.reject(pending_seller_request.id, "admin", "Fraud")

        await service.products_session.refresh(seed_data["seller"])
        assert seed_data["seller"].is_active is False
        service.vendor_session.execute.assert_called_once()


# ── idempotency / double-action guards ────────────────────────────────


@pytest.mark.asyncio
class TestDoubleAction:
    async def test_cannot_approve_twice(self, service, pending_product_request):
        await service.approve(pending_product_request.id, "admin")

        with pytest.raises(ConflictException):
            await service.approve(pending_product_request.id, "admin")

    async def test_cannot_reject_after_approve(self, service, pending_product_request):
        await service.approve(pending_product_request.id, "admin")

        with pytest.raises(ConflictException):
            await service.reject(pending_product_request.id, "admin", "Too late")
