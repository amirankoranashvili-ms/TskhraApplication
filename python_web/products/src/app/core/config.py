"""Application configuration for the products service.

Loads environment variables and provides centralized access to all
service-level settings such as database URLs, broker URLs, and search config.
"""

from pathlib import Path

from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Pydantic settings model for the products service.

    Reads configuration from environment variables and an optional .env file.
    Provides defaults for local development.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    SECRET_KEY: str = "change-me-in-production"
    TOKEN_URL: str = "/auth/token"
    APP_NAME: str = "Vipo Products"
    APP_VERSION: str = "1.0.0"

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "products-service"
    DATABASE_URL: str = "sqlite+aiosqlite:///./auth_db.db"
    REDIS_URL: str = "redis://localhost:6379"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_PASSWORD: str = ""

    BRAND_FIELD_ALIASES: list[str] = ["brand", "brand_id", "ბრენდი"]
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def assemble_db_url(cls, v: str, info: ValidationInfo) -> str:
        """Validate and transform the database URL for async SQLite support.

        Args:
            v: The raw DATABASE_URL value.
            info: Pydantic validation info containing previously validated fields.

        Returns:
            The adjusted database URL with async driver prefix and resolved path.
        """
        if v.startswith("sqlite://") and "aiosqlite" not in v:
            v = v.replace("sqlite://", "sqlite+aiosqlite://")

        if v.startswith("sqlite+aiosqlite:///./"):
            base_dir = info.data.get("BASE_DIR")
            path = v.replace("sqlite+aiosqlite:///./", "")
            return f"sqlite+aiosqlite:///{base_dir}/{path}"
        return v


# Singleton instance
settings = Settings()
