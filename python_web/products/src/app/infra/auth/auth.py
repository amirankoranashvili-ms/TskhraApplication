from backend_common.auth import create_keycloak_validator
from src.app.core.config import settings

oauth2_scheme, get_current_user_id = create_keycloak_validator(
    settings.KEYCLOAK_URL,
    settings.KEYCLOAK_REALM,
)
