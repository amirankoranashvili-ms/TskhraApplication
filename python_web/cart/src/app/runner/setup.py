import os
from contextlib import asynccontextmanager
from pathlib import Path

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend_common.database.migration import run_migrations
from backend_common.error_handlers import register_exception_handlers
from backend_common.logging import setup_logging
from backend_common.middleware import RequestLoggingMiddleware

from src.app.core.config import settings

ALEMBIC_INI = Path(__file__).resolve().parent.parent.parent.parent / "alembic.ini"
from src.app.core.facades.catalog_facade import CatalogFacade
from src.app.infra.database.config import engine
from src.app.infra.web.controllers.cart_controller import cart_router
from src.app.infra.web.dependables import init_cart_deps


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations(ALEMBIC_INI, settings.DATABASE_URL.replace("+asyncpg", ""))

    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: __import__("json").dumps(v).encode(),
    )
    await producer.start()

    catalog_facade = CatalogFacade(catalog_service_url=settings.PRODUCTS_SERVICE_URL)

    init_cart_deps(producer=producer, catalog_facade=catalog_facade)

    yield

    await producer.stop()
    await engine.dispose()


def create_app() -> FastAPI:
    setup_logging(settings.APP_NAME)
    root_path = os.getenv("ROOT_PATH", "")
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        root_path=root_path,
    )

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
    app.include_router(cart_router)

    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok"}

    return app
