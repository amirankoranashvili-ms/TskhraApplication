from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Admin Panel"
    APP_VERSION: str = "0.1.0"
    CORS_ORIGINS: list[str] = []

    PRODUCTS_DATABASE_URL: str
    VENDOR_DATABASE_URL: str

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    SECRET_KEY: str
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    SESSION_HTTPS_ONLY: bool = True

    UPLOAD_DIR: Path = Path("/app/uploads")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
