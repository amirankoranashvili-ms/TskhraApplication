import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from aiokafka import AIOKafkaProducer
from backend_common.database.migration import run_migrations
from backend_common.error_handlers import register_exception_handlers
from backend_common.logging import setup_logging
from backend_common.middleware import RequestLoggingMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.app.core.config import settings

ALEMBIC_INI = Path(__file__).resolve().parent.parent.parent.parent / "alembic.ini"
from src.app.infra.broker.consumer import VendorReplyConsumer
from src.app.infra.broker.publisher import KafkaEventPublisher, ProductEventPublisher
from src.app.infra.http_client.catalog_client import (
    close_catalog_http_client,
    init_catalog_http_client,
)
from src.app.infra.web.controllers.order_controller import vendor_orders_api
from src.app.infra.web.controllers.vendor_controller import (
    sellers_api,
    vendor_products_api,
)
from src.app.infra.web.dependables import (
    close_iban_http_client,
    init_iban_http_client,
    init_publisher,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations(ALEMBIC_INI, settings.DATABASE_URL.replace("+asyncpg", ""))

    init_catalog_http_client()
    init_iban_http_client()

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await producer.start()

    kafka_publisher = KafkaEventPublisher(producer)
    init_publisher(ProductEventPublisher(kafka_publisher))

    consumer = VendorReplyConsumer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    )
    await consumer.start()

    yield

    await consumer.stop()
    await producer.stop()
    await close_catalog_http_client()
    await close_iban_http_client()


def create_app() -> FastAPI:
    setup_logging(settings.APP_NAME)
    root_path = os.getenv("ROOT_PATH", "")
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        root_path=root_path,
    )

    app.include_router(sellers_api)
    app.include_router(vendor_products_api)
    app.include_router(vendor_orders_api)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://elegant-empanada-7041fb.netlify.app",
            "https://unfleeced-ariana-uncried.ngrok-free.dev",
            "http://localhost:4200",
            "http://0.0.0.0:8001",
            "http://0.0.0.0:8002",
            "https://vipo-web-app.vercel.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)

    return app
