import logging
import threading
from pathlib import Path

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def run_migrations(alembic_ini_path: str | Path, database_url: str) -> None:
    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    errors: list[Exception] = []

    def _run_in_thread() -> None:
        try:
            command.upgrade(alembic_cfg, "head")
        except Exception as exc:
            errors.append(exc)

    # env.py uses asyncio.run() which fails inside a running event loop.
    # Running alembic in a separate thread gives it a clean loop.
    thread = threading.Thread(target=_run_in_thread)
    thread.start()
    thread.join()

    if errors:
        logger.exception("Failed to apply database migrations")
        raise errors[0]

    logger.info("Database migrations applied successfully.")
