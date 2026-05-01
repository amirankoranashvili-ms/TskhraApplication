"""JWT authentication setup for the payment service."""

from backend_common.auth import create_jwt_validator

from src.app.core.config import settings

oauth2_scheme, get_current_user_id = create_jwt_validator(
    settings.SECRET_KEY, settings.TOKEN_URL
)
