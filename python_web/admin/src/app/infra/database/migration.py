"""Alembic database migration runner."""

from pathlib import Path

from alembic import command
from alembic.config import Config

from src.app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
ALEMBIC_INI_PATH = BASE_DIR / "alembic.ini"


def run_migrations():
    """Run all pending Alembic migrations against the admin database."""
    alembic_cfg = Config(str(ALEMBIC_INI_PATH))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.PRODUCTS_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
