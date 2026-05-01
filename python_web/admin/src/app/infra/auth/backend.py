"""Authentication backend for the SQLAdmin panel."""

import hmac
import logging
import time

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.app.core.config import settings
from src.app.core.constants import SessionKeys

logger = logging.getLogger(__name__)

_failed_attempts: dict[str, tuple[int, float]] = {}
_MAX_ATTEMPTS = 5
_LOCKOUT_SECONDS = 300  # seconds
_CLEANUP_THRESHOLD = 100


def _cleanup_expired_attempts() -> None:
    """Remove expired entries from the failed attempts dict to prevent memory growth."""
    now = time.time()
    expired = [
        ip
        for ip, (_, since) in _failed_attempts.items()
        if now - since > _LOCKOUT_SECONDS
    ]
    for ip in expired:
        del _failed_attempts[ip]


class AdminAuthBackend(AuthenticationBackend):
    """Simple username/password authentication backend for the admin panel."""

    async def login(self, request: Request) -> bool:
        """Authenticate an admin user from the login form.

        Args:
            request: The incoming HTTP request containing form data.

        Returns:
            True if credentials are valid, False otherwise.
        """
        if len(_failed_attempts) > _CLEANUP_THRESHOLD:
            _cleanup_expired_attempts()

        ip = request.client.host if request.client else "unknown"
        now = time.time()

        count, since = _failed_attempts.get(ip, (0, now))
        if now - since > _LOCKOUT_SECONDS:
            count = 0
            since = now

        if count >= _MAX_ATTEMPTS:
            logger.warning("Login blocked for IP %s: too many failed attempts", ip)
            return False

        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))

        valid = hmac.compare_digest(
            username, settings.ADMIN_USERNAME
        ) and hmac.compare_digest(password, settings.ADMIN_PASSWORD)

        if valid:
            _failed_attempts.pop(ip, None)
            request.session[SessionKeys.AUTHENTICATED] = True
            request.session[SessionKeys.USERNAME] = username
            return True

        _failed_attempts[ip] = (count + 1, since)
        logger.warning("Failed login attempt for user %s from %s", username, ip)
        return False

    async def logout(self, request: Request) -> bool:
        """Clear the session to log out the admin user.

        Args:
            request: The incoming HTTP request.

        Returns:
            Always True.
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> RedirectResponse | bool:
        """Check whether the current request is authenticated.

        Args:
            request: The incoming HTTP request.

        Returns:
            True if authenticated, or a RedirectResponse to the login page.
        """
        if request.session.get(SessionKeys.AUTHENTICATED):
            return True
        return RedirectResponse(request.url_for("admin:login"), status_code=302)
