"""HTTP routes for approving and rejecting verification requests."""

import hmac
import logging
import secrets
from contextlib import asynccontextmanager
from functools import wraps
from pathlib import Path
from typing import Callable

import sqladmin
from fastapi import FastAPI, Request
from sqladmin import Admin
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from src.app.core.constants import SessionKeys
from src.app.core.verification_service import VerificationService
from src.app.infra.database.engines import vendor_engine
from src.app.infra.database.session import async_session

logger = logging.getLogger(__name__)

ADMIN_LOGIN_URL = "/admin/login"
VERIFICATION_LIST_URL = "/admin/verification-request-db/list"
VERIFICATION_REJECT_TEMPLATE = "verification_reject.html"

vendor_session_factory = async_sessionmaker(
    vendor_engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def _verification_service(publisher=None):
    """Create a VerificationService with properly scoped database sessions.

    Args:
        publisher: Optional event publisher for broker notifications.

    Yields:
        A configured VerificationService instance.
    """
    async with (
        async_session() as products_session,
        vendor_session_factory() as vendor_session,
    ):
        yield VerificationService(products_session, vendor_session, publisher)


def require_auth(func: Callable):
    """Decorator that redirects unauthenticated requests to the login page.

    Args:
        func: The async route handler to wrap.

    Returns:
        The wrapped handler that enforces authentication.
    """

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if not request.session.get(SessionKeys.AUTHENTICATED):
            return RedirectResponse(ADMIN_LOGIN_URL, status_code=302)
        return await func(request, *args, **kwargs)

    return wrapper


def _get_publisher(request: Request):
    return getattr(request.app.state, "publisher", None)


def _set_csrf_token(request: Request) -> str:
    """Generate a CSRF token and store it in the session."""
    token = secrets.token_hex(32)
    request.session["csrf_token"] = token
    return token


def _validate_csrf(request: Request, form) -> bool:
    """Check the form CSRF token against the session token."""
    form_csrf = str(form.get("csrf_token", ""))
    session_csrf = request.session.get("csrf_token", "")
    return bool(form_csrf) and hmac.compare_digest(form_csrf, session_csrf)


def register_verification_routes(app: FastAPI, admin: Admin, templates_dir: str):
    """Register the verification approve/reject routes on the FastAPI app.

    Args:
        app: The FastAPI application instance.
        admin: The SQLAdmin instance used for template context.
        templates_dir: Path to the directory containing Jinja2 templates.
    """
    sqladmin_templates_dir = str(Path(sqladmin.__file__).parent / "templates")
    templates = Jinja2Templates(directory=[templates_dir, sqladmin_templates_dir])
    templates.env.globals["get_flashed_messages"] = lambda *args, **kwargs: []

    async def _render_reject_form(request, request_id, error=None):
        async with _verification_service() as service:
            vr, product = await service.get_with_product(request_id)
        context = {
            "admin": admin,
            "verification_request": vr,
            "product": product,
        }
        if error:
            context["error"] = error
        return templates.TemplateResponse(
            request, VERIFICATION_REJECT_TEMPLATE, context=context
        )

    @app.get("/verification/{request_id}/approve", include_in_schema=False)
    @require_auth
    async def approve_verification_form(request: Request, request_id: int):
        csrf_token = _set_csrf_token(request)

        async with _verification_service() as service:
            _, product = await service.get_with_product(request_id)

        product_info = ""
        if product:
            product_info = (
                f"<p><strong>Product:</strong> {product.title} (SKU: {product.sku})</p>"
            )

        return HTMLResponse(
            f"""<!DOCTYPE html>
            <html>
            <head><title>Confirm Approve</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"></head>
            <body><div class="container mt-5">
            <div class="card"><div class="card-body">
            <h4 class="card-title">Confirm Approval</h4>
            <p>Are you sure you want to approve verification request <strong>#{request_id}</strong>?</p>
            {product_info}
            <form method="post" action="/verification/{request_id}/approve">
            <input type="hidden" name="csrf_token" value="{csrf_token}">
            <button type="submit" class="btn btn-success me-2">Confirm Approve</button>
            <a href="{VERIFICATION_LIST_URL}" class="btn btn-secondary">Cancel</a>
            </form>
            </div></div></div></body></html>"""
        )

    @app.post("/verification/{request_id}/approve", include_in_schema=False)
    @require_auth
    async def approve_verification(request: Request, request_id: int):
        form = await request.form()
        if not _validate_csrf(request, form):
            return RedirectResponse(VERIFICATION_LIST_URL, status_code=302)

        admin_username = request.session.get(SessionKeys.USERNAME, "unknown")

        async with _verification_service(_get_publisher(request)) as service:
            try:
                await service.approve(request_id, admin_username)
            except ValueError as e:
                logger.warning("Approve failed for request %s: %s", request_id, e)
            except Exception as e:
                logger.error(
                    "Error approving verification request %s: %s",
                    request_id,
                    e,
                    exc_info=True,
                )

        return RedirectResponse(VERIFICATION_LIST_URL, status_code=302)

    @app.get("/verification/{request_id}/reject", include_in_schema=False)
    @require_auth
    async def reject_verification_form(request: Request, request_id: int):
        _set_csrf_token(request)
        return await _render_reject_form(request, request_id)

    @app.post("/verification/{request_id}/reject", include_in_schema=False)
    @require_auth
    async def reject_verification(request: Request, request_id: int):
        admin_username = request.session.get(SessionKeys.USERNAME, "unknown")
        form = await request.form()
        rejection_reason = form.get("rejection_reason", "").strip()

        if not _validate_csrf(request, form):
            return await _render_reject_form(
                request, request_id, error="Invalid CSRF token. Please try again."
            )
        if not rejection_reason:
            return await _render_reject_form(
                request, request_id, error="Rejection reason is required."
            )

        async with _verification_service(_get_publisher(request)) as service:
            try:
                await service.reject(request_id, admin_username, rejection_reason)
            except ValueError as e:
                logger.warning("Reject failed for request %s: %s", request_id, e)
            except Exception as e:
                logger.error(
                    "Error rejecting verification request %s: %s",
                    request_id,
                    e,
                    exc_info=True,
                )

        return RedirectResponse(VERIFICATION_LIST_URL, status_code=302)
