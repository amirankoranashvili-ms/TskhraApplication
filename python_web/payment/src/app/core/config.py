"""Payment service configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings populated from environment variables and .env file."""

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    SECRET_KEY: str
    TOKEN_URL: str = "/auth/token"
    APP_NAME: str = "Payment Service"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    REDIS_URL: str = "redis://localhost:6379/0"

    PAYMENT_PROVIDER: str = "mock"  # "mock", "stripe", or "keepz"
    STRIPE_SECRET_KEY: str = ""
    KEEPZ_IDENTIFIER: str = ""
    KEEPZ_INTEGRATOR_ID: str = ""
    KEEPZ_RECEIVER_ID: str = ""
    KEEPZ_RECEIVER_TYPE: str = "BRANCH"
    KEEPZ_RSA_PUBLIC_KEY: str = ""
    KEEPZ_RSA_PRIVATE_KEY: str = ""
    KEEPZ_BASE_URL: str = "https://gateway.keepz.me/ecommerce-service"
    KEEPZ_CALLBACK_URL: str = ""
    ALLOWED_REDIRECT_ORIGINS: str = ""
    CORS_ALLOWED_ORIGINS: str = ""

    @property
    def keepz_allowed_redirect_origins(self) -> list[str]:
        if not self.ALLOWED_REDIRECT_ORIGINS:
            return []
        return [
            o.strip() for o in self.ALLOWED_REDIRECT_ORIGINS.split(",") if o.strip()
        ]

    @property
    def cors_allowed_origins(self) -> list[str]:
        if not self.CORS_ALLOWED_ORIGINS:
            return ["*"]
        return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
