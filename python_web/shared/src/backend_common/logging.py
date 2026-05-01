"""Structured logging configuration for all microservices.

Provides JSON-formatted log output with correlation ID support,
designed to work with Loki log aggregation via the Docker logging driver.
"""

import json
import logging
import sys
import uuid
from contextvars import ContextVar

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """Log formatter that outputs structured JSON lines.

    Each log line includes timestamp, level, logger name, message,
    service name, and correlation request_id when available.
    """

    def __init__(self, service_name: str = "unknown") -> None:
        """Initialize the JSON formatter.

        Args:
            service_name: Name of the service emitting logs.
        """
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            A single-line JSON string.
        """
        log_data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%03d"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
        }

        req_id = request_id_ctx.get()
        if req_id:
            log_data["request_id"] = req_id

        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(service_name: str, level: str = "INFO") -> None:
    """Configure structured JSON logging for a service.

    Replaces the root logger's handlers with a single stdout handler
    using the JSON formatter. Also quiets noisy third-party loggers.

    Args:
        service_name: Name of the service, included in every log line.
        level: The root log level (default INFO).
    """
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter(service_name=service_name))
    root.addHandler(handler)

    # Quiet noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aio_pika").setLevel(logging.WARNING)
    logging.getLogger("aiormq").setLevel(logging.WARNING)
    logging.getLogger("hpack").setLevel(logging.WARNING)


def generate_request_id() -> str:
    """Generate a new unique request ID.

    Returns:
        A short UUID string suitable for correlation.
    """
    return uuid.uuid4().hex[:12]
