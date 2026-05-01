"""FastAPI application factory and admin view registration."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from backend_common.logging import setup_logging
from backend_common.middleware import RequestLoggingMiddleware
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqladmin import Admin
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from src.app.core.config import settings
from src.app.infra.auth.backend import AdminAuthBackend
from src.app.infra.broker.connection import (
    KafkaEventPublisher,
    close_kafka_producer,
    init_kafka_producer,
)
from src.app.infra.broker.consumer import VerificationConsumer
from src.app.infra.database.engines import (
    products_engine,
    vendor_engine,
)
from src.app.infra.database.session import async_session
from src.app.infra.web.controllers.verification_controller import (
    register_verification_routes,
)
from src.app.infra.web.views.product_views import (
    BrandAdmin,
    CategoryAdmin,
    CategoryFieldAdmin,
    FieldAdmin,
    FieldGroupAdmin,
    FieldOptionAdmin,
    PlatformSellerAdmin,
    ProductAdmin,
    ProductFieldValueAdmin,
    ProductImageAdmin,
    SupplierAdmin,
    VerificationRequestAdmin,
)

logger = logging.getLogger(__name__)

TEMPLATES_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "templates")


def register_admin_views(admin: Admin):
    """Register all SQLAdmin model views with the admin instance.

    Args:
        admin: The SQLAdmin Admin instance to attach views to.
    """
    admin.add_view(CategoryAdmin)
    admin.add_view(BrandAdmin)
    admin.add_view(SupplierAdmin)
    admin.add_view(PlatformSellerAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(ProductImageAdmin)
    admin.add_view(FieldGroupAdmin)
    admin.add_view(FieldAdmin)
    admin.add_view(FieldOptionAdmin)
    admin.add_view(CategoryFieldAdmin)
    admin.add_view(ProductFieldValueAdmin)

    admin.add_view(VerificationRequestAdmin)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    producer = await init_kafka_producer()
    app.state.publisher = KafkaEventPublisher(producer)

    consumer = VerificationConsumer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    )
    await consumer.start()

    yield

    await consumer.stop()
    await close_kafka_producer()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        A fully configured FastAPI application with admin panel,
        middleware, static files, and verification routes.
    """
    setup_logging(settings.APP_NAME)
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    @app.get("/health", include_in_schema=False)
    async def health():
        health_status = {"status": "ok", "databases": {}}
        overall_healthy = True

        db_configs = {
            "products": products_engine,
            "vendor": vendor_engine,
        }

        for db_name, db_engine in db_configs.items():
            try:
                async with db_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                health_status["databases"][db_name] = "healthy"
            except Exception as e:
                logger.error("Database %s health check failed: %s", db_name, e)
                health_status["databases"][db_name] = "unhealthy"
                overall_healthy = False

        if not overall_healthy:
            health_status["status"] = "degraded"
            return JSONResponse(content=health_status, status_code=503)

        return health_status

    class SecurityHeadersMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
                "img-src 'self' /uploads/ data:; "
                "font-src 'self' cdn.jsdelivr.net; "
                "frame-ancestors 'none'"
            )
            if settings.SESSION_HTTPS_ONLY:
                response.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains"
                )
            return response

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        https_only=settings.SESSION_HTTPS_ONLY,
        same_site="lax",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/uploads",
        StaticFiles(directory=str(settings.UPLOAD_DIR)),
        name="uploads",
    )

    auth_backend = AdminAuthBackend(secret_key=settings.SECRET_KEY)

    admin = Admin(
        app,
        engine=products_engine,
        session_maker=async_session,
        authentication_backend=auth_backend,
        title="Admin Panel",
        templates_dir=TEMPLATES_DIR,
        base_url="/admin",
    )

    admin.templates.env.globals["get_flashed_messages"] = lambda *args, **kwargs: []

    register_admin_views(admin)
    register_verification_routes(app, admin, TEMPLATES_DIR)

    return app
