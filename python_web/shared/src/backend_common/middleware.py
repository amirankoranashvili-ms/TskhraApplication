"""HTTP request/response logging middleware.

Adds a correlation request_id to every request, logs request start
and completion with timing, status code, and path information.
"""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend_common.logging import generate_request_id, request_id_ctx

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every HTTP request and response.

    Assigns a unique request_id to each request, stores it in a
    context variable for downstream log correlation, and logs the
    method, path, status code, and duration.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request with logging.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or route handler.

        Returns:
            The HTTP response.
        """
        if request.url.path == "/health":
            return await call_next(request)

        req_id = request.headers.get("X-Request-ID") or generate_request_id()
        token = request_id_ctx.set(req_id)

        start = time.perf_counter()
        method = request.method
        path = request.url.path

        logger.info(
            "%s %s started",
            method,
            path,
            extra={"extra_fields": {"method": method, "path": path}},
        )

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start) * 1000, 1)

            log_fn = logger.warning if response.status_code >= 400 else logger.info
            log_fn(
                "%s %s %d %.1fms",
                method,
                path,
                response.status_code,
                duration_ms,
                extra={
                    "extra_fields": {
                        "method": method,
                        "path": path,
                        "status": response.status_code,
                        "duration_ms": duration_ms,
                    }
                },
            )

            response.headers["X-Request-ID"] = req_id
            return response
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            logger.exception(
                "%s %s failed after %.1fms",
                method,
                path,
                duration_ms,
                extra={
                    "extra_fields": {
                        "method": method,
                        "path": path,
                        "duration_ms": duration_ms,
                    }
                },
            )
            raise
        finally:
            request_id_ctx.reset(token)
