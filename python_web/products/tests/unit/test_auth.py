import pytest
from unittest.mock import patch
from uuid import uuid4

from jose import jwt

from backend_common.exceptions import NotAuthenticatedException

ALGORITHM = "HS256"


@pytest.mark.asyncio
async def test_get_current_user_id_valid():
    from src.app.infra.auth.auth import get_current_user_id
    from src.app.core.config import settings

    user_id = str(uuid4())
    token = jwt.encode(
        {"sub": user_id, "type": "access"},
        settings.SECRET_KEY or "test-secret",
        algorithm=ALGORITHM,
    )

    with patch.object(settings, "SECRET_KEY", settings.SECRET_KEY or "test-secret"):
        result = await get_current_user_id(token)
        assert str(result) == user_id


@pytest.mark.asyncio
async def test_get_current_user_id_invalid_token():
    from src.app.infra.auth.auth import get_current_user_id

    with pytest.raises(NotAuthenticatedException):
        await get_current_user_id("invalid.token.here")


@pytest.mark.asyncio
async def test_get_current_user_id_no_sub():
    from src.app.infra.auth.auth import get_current_user_id
    from src.app.core.config import settings

    token = jwt.encode(
        {"type": "access"},
        settings.SECRET_KEY or "test-secret",
        algorithm=ALGORITHM,
    )

    with patch.object(settings, "SECRET_KEY", settings.SECRET_KEY or "test-secret"):
        with pytest.raises(NotAuthenticatedException):
            await get_current_user_id(token)


@pytest.mark.asyncio
async def test_get_current_user_id_wrong_token_type():
    from src.app.infra.auth.auth import get_current_user_id
    from src.app.core.config import settings

    token = jwt.encode(
        {"sub": str(uuid4()), "type": "refresh"},
        settings.SECRET_KEY or "test-secret",
        algorithm=ALGORITHM,
    )

    with patch.object(settings, "SECRET_KEY", settings.SECRET_KEY or "test-secret"):
        with pytest.raises(NotAuthenticatedException):
            await get_current_user_id(token)
