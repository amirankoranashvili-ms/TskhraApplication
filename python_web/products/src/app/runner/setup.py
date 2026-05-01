import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend_common.error_handlers import register_exception_handlers
from backend_common.logging import setup_logging
from backend_common.middleware import RequestLoggingMiddleware
from src.app.core.config import settings
from src.app.infra.broker.connection import (
    init_kafka_producer,
    create_kafka_consumer,
    close_kafka_producer,
)
from src.app.infra.broker.consumer import PRODUCT_TOPIC, start_product_consumer
from src.app.infra.search.client import setup_elasticsearch_index
from src.app.infra.web.controllers.products_controller import products_api, internal_api


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_kafka_producer()
    consumer = await create_kafka_consumer(PRODUCT_TOPIC)
    consumer_task = asyncio.create_task(start_product_consumer(consumer))

    try:
        await setup_elasticsearch_index()
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning("Failed to setup Elasticsearch index: %s", e)

    yield

    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await close_kafka_producer()


def create_app() -> FastAPI:
    setup_logging(settings.APP_NAME)
    root_path = os.getenv("ROOT_PATH", "")
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        root_path=root_path,
    )

    app.include_router(products_api, tags=["Products"])
    app.include_router(internal_api)
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
