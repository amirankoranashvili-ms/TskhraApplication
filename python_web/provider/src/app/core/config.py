"""Configuration module for the Vendor Provider Service.

Loads application settings from environment variables and .env files
using pydantic-settings.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        BASE_DIR: Root directory of the application source.
        APP_NAME: Display name of the service.
        APP_VERSION: Semantic version string.
        SECRET_KEY: Secret key for JWT token validation.
        TOKEN_URL: OAuth2 token endpoint path.
        DATABASE_URL: PostgreSQL connection string.
        KAFKA_BOOTSTRAP_SERVERS: Kafka broker connection string.
        PRODUCTS_SERVICE_URL: Base URL of the catalog/products service.
        MINIO_ENDPOINT: MinIO server endpoint.
        MINIO_ACCESS_KEY: MinIO access key credential.
        MINIO_SECRET_KEY: MinIO secret key credential.
        MINIO_SECURE: Whether to use HTTPS for MinIO connections.
        MINIO_PUBLIC_URL: Public-facing URL for MinIO object access.
        MINIO_BUCKET: MinIO bucket name for product images.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    APP_NAME: str = "Vendor Provider Service"
    APP_VERSION: str = "1.0.0"
    KEYCLOAK_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "tskhra"

    DATABASE_URL: str
    TSKHRA_DATABASE_URL: str = "postgresql+asyncpg://admin:password@localhost:5432/tskhra_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    PRODUCTS_SERVICE_URL: str = "http://localhost:8004"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    # TODO: replace with external IP for production (match Java: http://10.227.164.247:9000)
    MINIO_PUBLIC_URL: str = "http://localhost:9000"
    MINIO_BUCKET: str = "product-images"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
