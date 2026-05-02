"""Configuration module for the cart service.

Loads application settings from environment variables and .env files
using pydantic-settings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings for the cart service.

    Reads configuration values from environment variables and an .env file,
    including database connection strings, service URLs, and resilience
    parameters for the catalog facade.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    APP_NAME: str = "Vipo Cart"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/cart_db"
    PRODUCTS_SERVICE_URL: str = "http://products_service:8004"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "tskhra"

    CATALOG_CIRCUIT_FAILURE_THRESHOLD: int = 5
    CATALOG_CIRCUIT_RECOVERY_TIMEOUT: int = 30
    CATALOG_RETRY_MAX_ATTEMPTS: int = 3
    CATALOG_RETRY_BACKOFF_BASE: float = 0.5
    CATALOG_BULKHEAD_MAX_CONCURRENT: int = 20
    CATALOG_BULKHEAD_MAX_WAIT: float = 5.0
    CATALOG_REQUEST_TIMEOUT: float = 5.0

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
