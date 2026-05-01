import pytest
from unittest.mock import AsyncMock, patch

from src.app.infra.broker.consumer import (
    _handle_seller_created,
    _handle_seller_updated,
    _handle_product_created,
    _handle_product_updated,
    _handle_product_deleted,
    CatalogEventConsumer,
    EVENT_HANDLERS,
)


@pytest.mark.asyncio
async def test_handle_seller_created():
    mock_db = AsyncMock()
    payload = {
        "supplier_id": 1,
        "name": "Seller",
        "user_id": "abc",
        "identification_number": "123",
        "legal_address": "Addr",
    }

    with (
        patch(
            "src.app.infra.broker.consumer.SqlAlchemySellerRepository"
        ) as MockSellerRepo,
        patch(
            "src.app.infra.broker.consumer.SqlAlchemyVerificationRequestRepository"
        ) as MockVRRepo,
    ):
        mock_seller = AsyncMock()
        MockSellerRepo.return_value = mock_seller
        mock_vr = AsyncMock()
        MockVRRepo.return_value = mock_vr

        await _handle_seller_created(mock_db, payload)

        mock_seller.create_seller.assert_awaited_once_with(payload)
        mock_vr.create_verification_request.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_seller_updated():
    mock_db = AsyncMock()
    payload = {
        "supplier_id": 1,
        "name": "Updated",
        "identification_number": "456",
        "legal_address": "New",
    }

    with (
        patch(
            "src.app.infra.broker.consumer.SqlAlchemySellerRepository"
        ) as MockSellerRepo,
        patch(
            "src.app.infra.broker.consumer.SqlAlchemyVerificationRequestRepository"
        ) as MockVRRepo,
    ):
        mock_seller = AsyncMock()
        MockSellerRepo.return_value = mock_seller
        mock_vr = AsyncMock()
        MockVRRepo.return_value = mock_vr

        await _handle_seller_updated(mock_db, payload)

        mock_seller.update_seller.assert_awaited_once()
        mock_vr.create_verification_request.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_product_created_success():
    mock_db = AsyncMock()
    payload = {
        "task_id": "t1",
        "supplier_id": 1,
        "is_provider": True,
        "category_id": 1,
        "brand_id": 1,
        "title": "New",
        "price": 10.0,
        "sku": "S1",
    }

    with (
        patch("src.app.infra.broker.consumer.SqlAlchemyProductRepository"),
        patch(
            "src.app.infra.broker.consumer.HandleProductUploadInteractor"
        ) as MockInteractor,
        patch(
            "src.app.infra.broker.consumer.SqlAlchemyVerificationRequestRepository"
        ) as MockVRRepo,
        patch("src.app.infra.broker.consumer.ProviderReplyPublisher") as mock_publisher,
    ):
        mock_interactor = AsyncMock()
        mock_interactor.execute.return_value = {
            "task_id": "t1",
            "product_id": 42,
            "supplier_id": 1,
            "status": "SUCCESS",
            "error_message": None,
        }
        MockInteractor.return_value = mock_interactor
        MockVRRepo.return_value = AsyncMock()
        mock_publisher.send_reply = AsyncMock()

        await _handle_product_created(mock_db, payload)

        mock_interactor.execute.assert_awaited_once()
        mock_publisher.send_reply.assert_awaited_once()
        MockVRRepo.return_value.create_verification_request.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_product_created_failed():
    mock_db = AsyncMock()
    payload = {
        "task_id": "t1",
        "supplier_id": 1,
        "is_provider": True,
        "category_id": 1,
        "brand_id": 1,
        "title": "New",
        "price": 10.0,
        "sku": "S1",
    }

    with (
        patch("src.app.infra.broker.consumer.SqlAlchemyProductRepository"),
        patch(
            "src.app.infra.broker.consumer.HandleProductUploadInteractor"
        ) as MockInteractor,
        patch(
            "src.app.infra.broker.consumer.SqlAlchemyVerificationRequestRepository"
        ) as MockVRRepo,
        patch("src.app.infra.broker.consumer.ProviderReplyPublisher") as mock_publisher,
    ):
        mock_interactor = AsyncMock()
        mock_interactor.execute.return_value = {
            "task_id": "t1",
            "product_id": None,
            "supplier_id": 1,
            "status": "FAILED",
            "error_message": "error",
        }
        MockInteractor.return_value = mock_interactor
        mock_publisher.send_reply = AsyncMock()

        await _handle_product_created(mock_db, payload)

        MockVRRepo.return_value.create_verification_request.assert_not_called()
        mock_publisher.send_reply.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_product_updated_success():
    mock_db = AsyncMock()
    payload = {"task_id": "t2", "product_id": 1, "supplier_id": 1, "title": "Updated"}

    with (
        patch("src.app.infra.broker.consumer.SqlAlchemyProductRepository"),
        patch(
            "src.app.infra.broker.consumer.HandleProductUpdateInteractor"
        ) as MockInteractor,
        patch(
            "src.app.infra.broker.consumer.SqlAlchemyVerificationRequestRepository"
        ) as MockVRRepo,
        patch("src.app.infra.broker.consumer.ProviderReplyPublisher") as mock_publisher,
    ):
        mock_interactor = AsyncMock()
        mock_interactor.execute.return_value = {
            "task_id": "t2",
            "product_id": 1,
            "supplier_id": 1,
            "status": "SUCCESS",
            "error_message": None,
        }
        MockInteractor.return_value = mock_interactor
        MockVRRepo.return_value = AsyncMock()
        mock_publisher.send_reply = AsyncMock()

        await _handle_product_updated(mock_db, payload)

        mock_interactor.execute.assert_awaited_once()
        mock_publisher.send_reply.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_product_updated_failed():
    mock_db = AsyncMock()
    payload = {"task_id": "t2", "product_id": 1, "supplier_id": 1, "title": "Updated"}

    with (
        patch("src.app.infra.broker.consumer.SqlAlchemyProductRepository"),
        patch(
            "src.app.infra.broker.consumer.HandleProductUpdateInteractor"
        ) as MockInteractor,
        patch(
            "src.app.infra.broker.consumer.SqlAlchemyVerificationRequestRepository"
        ) as MockVRRepo,
        patch("src.app.infra.broker.consumer.ProviderReplyPublisher") as mock_publisher,
    ):
        mock_interactor = AsyncMock()
        mock_interactor.execute.return_value = {
            "task_id": "t2",
            "product_id": 1,
            "supplier_id": 1,
            "status": "FAILED",
            "error_message": "err",
        }
        MockInteractor.return_value = mock_interactor
        mock_publisher.send_reply = AsyncMock()

        await _handle_product_updated(mock_db, payload)

        MockVRRepo.return_value.create_verification_request.assert_not_called()


@pytest.mark.asyncio
async def test_handle_product_deleted():
    mock_db = AsyncMock()
    payload = {"product_id": 5, "supplier_id": 1}

    with patch("src.app.infra.broker.consumer.SqlAlchemyProductRepository") as MockRepo:
        mock_repo = AsyncMock()
        MockRepo.return_value = mock_repo

        await _handle_product_deleted(mock_db, payload)

        mock_repo.delete_product.assert_awaited_once_with(5, 1)


@pytest.mark.asyncio
async def test_handle_message_dispatches_to_handler():
    consumer = CatalogEventConsumer.__new__(CatalogEventConsumer)
    mock_db = AsyncMock()
    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_db)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

    with (
        patch(
            "src.app.infra.broker.consumer.AsyncSessionLocal",
            return_value=mock_session_ctx,
        ),
        patch(
            "src.app.infra.broker.consumer.SqlAlchemySellerRepository"
        ) as MockSellerRepo,
        patch(
            "src.app.infra.broker.consumer.SqlAlchemyVerificationRequestRepository"
        ) as MockVRRepo,
    ):
        MockSellerRepo.return_value = AsyncMock()
        MockVRRepo.return_value = AsyncMock()

        await consumer.handle_message(
            "seller.created", {"supplier_id": 1, "name": "Test"}
        )

        MockSellerRepo.return_value.create_seller.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_message_unknown_routing_key():
    consumer = CatalogEventConsumer.__new__(CatalogEventConsumer)

    await consumer.handle_message("unknown.key", {"data": 1})


@pytest.mark.asyncio
async def test_event_handlers_keys():
    expected = {
        "seller.created",
        "seller.updated",
        "product.created",
        "product.updated",
        "product.deleted",
        "product.verified",
    }
    assert set(EVENT_HANDLERS.keys()) == expected
