from uuid import UUID

from backend_common.auth import create_keycloak_validator
from fastapi import Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.app.core.config import settings

oauth2_scheme, get_current_user_id = create_keycloak_validator(
    settings.KEYCLOAK_URL,
    settings.KEYCLOAK_REALM,
)

_tskhra_engine = create_async_engine(settings.TSKHRA_DATABASE_URL, pool_size=2)


async def require_kyc_verified(
    user_id: UUID = Depends(get_current_user_id),
) -> None:
    async with _tskhra_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT kyc_status FROM users WHERE keycloak_id = :kid"),
            {"kid": user_id},
        )
        row = result.fetchone()

    if not row or row[0] != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="KYC verification required",
        )
