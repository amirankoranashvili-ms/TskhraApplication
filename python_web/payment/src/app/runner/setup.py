import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from aiokafka import AIOKafkaProducer
from backend_common.cache.client import create_redis_client
from backend_common.cache.service import CacheService
from backend_common.error_handlers import (
    ERROR_CODE_TO_HTTP,
    register_exception_handlers,
)
from backend_common.logging import setup_logging
from backend_common.middleware import RequestLoggingMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend_common.database.migration import run_migrations

from src.app.core.config import settings

ALEMBIC_INI = Path(__file__).resolve().parent.parent.parent.parent / "alembic.ini"
from src.app.infra.broker.consumer import CheckoutEventConsumer, VendorStatusConsumer
from src.app.infra.broker.publisher import KafkaEventPublisher
from src.app.infra.database.config import engine
from src.app.infra.gateway.keepz_gateway import KeepZPaymentGateway
from src.app.infra.gateway.mock_gateway import MockPaymentGateway
from src.app.infra.gateway.stripe_gateway import StripePaymentGateway
from src.app.infra.web.controllers.internal_controller import internal_router
from src.app.infra.web.controllers.payment_controller import payment_router
from src.app.infra.web.dependables import init_payment_deps


def _create_payment_gateway():
    if settings.PAYMENT_PROVIDER == "stripe" and settings.STRIPE_SECRET_KEY:
        return StripePaymentGateway(secret_key=settings.STRIPE_SECRET_KEY)
    if settings.PAYMENT_PROVIDER == "keepz" and settings.KEEPZ_IDENTIFIER:
        return KeepZPaymentGateway(
            identifier=settings.KEEPZ_IDENTIFIER,
            integrator_id=settings.KEEPZ_INTEGRATOR_ID,
            receiver_id=settings.KEEPZ_RECEIVER_ID,
            receiver_type=settings.KEEPZ_RECEIVER_TYPE,
            rsa_public_key=settings.KEEPZ_RSA_PUBLIC_KEY,
            rsa_private_key=settings.KEEPZ_RSA_PRIVATE_KEY,
            base_url=settings.KEEPZ_BASE_URL,
            callback_url=settings.KEEPZ_CALLBACK_URL,
        )
    return MockPaymentGateway()


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations(ALEMBIC_INI, settings.DATABASE_URL.replace("+asyncpg", ""))

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode(),
    )
    await producer.start()

    publisher = KafkaEventPublisher(producer)

    gateway = _create_payment_gateway()

    redis_client = create_redis_client(settings.REDIS_URL)
    cache_service = CacheService(redis_client)

    init_payment_deps(
        publisher=publisher, payment_gateway=gateway, cache_service=cache_service
    )

    checkout_consumer = CheckoutEventConsumer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        publisher=publisher,
        payment_gateway=gateway,
        cache_service=cache_service,
    )
    await checkout_consumer.start()

    vendor_status_consumer = VendorStatusConsumer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    )
    await vendor_status_consumer.start()

    yield

    await checkout_consumer.stop()
    await vendor_status_consumer.stop()
    await producer.stop()
    await engine.dispose()


def create_app() -> FastAPI:
    setup_logging(settings.APP_NAME)
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        root_path=os.getenv("ROOT_PATH", ""),
        lifespan=lifespan,
    )

    cors_origins = settings.cors_allowed_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=cors_origins != ["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)

    ERROR_CODE_TO_HTTP["PAYMENT_FAILED"] = 500
    ERROR_CODE_TO_HTTP["REFUND_FAILED"] = 500
    ERROR_CODE_TO_HTTP["CONFLICT"] = 409

    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok"}

    app.include_router(payment_router)
    app.include_router(internal_router)

    return app
