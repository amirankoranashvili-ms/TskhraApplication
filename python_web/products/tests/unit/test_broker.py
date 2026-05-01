import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_init_kafka_producer():
    mock_producer = AsyncMock()

    with patch("src.app.infra.broker.connection.AIOKafkaProducer", return_value=mock_producer):
        import src.app.infra.broker.connection as broker_mod

        result = await broker_mod.init_kafka_producer()

        assert result is mock_producer
        mock_producer.start.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_kafka_producer_with_producer():
    mock_producer = AsyncMock()

    import src.app.infra.broker.connection as broker_mod
    broker_mod.producer = mock_producer

    await broker_mod.close_kafka_producer()

    mock_producer.stop.assert_awaited_once()
    assert broker_mod.producer is None


@pytest.mark.asyncio
async def test_close_kafka_producer_no_producer():
    import src.app.infra.broker.connection as broker_mod
    broker_mod.producer = None

    await broker_mod.close_kafka_producer()


@pytest.mark.asyncio
async def test_publisher_send_reply():
    mock_producer = AsyncMock()

    with patch("src.app.infra.broker.connection.producer", mock_producer):
        from src.app.infra.broker.publisher import ProviderReplyPublisher

        await ProviderReplyPublisher.send_reply(
            status="SUCCESS",
            payload={"task_id": "t1"},
            action="upload",
        )

        mock_producer.send_and_wait.assert_awaited_once()


@pytest.mark.asyncio
async def test_publisher_send_reply_no_producer():
    with patch("src.app.infra.broker.connection.producer", None):
        from src.app.infra.broker.publisher import ProviderReplyPublisher

        await ProviderReplyPublisher.send_reply(
            status="SUCCESS",
            payload={"task_id": "t1"},
        )
