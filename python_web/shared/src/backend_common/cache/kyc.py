from uuid import UUID

import redis.asyncio as aioredis

_KYC_KEY = "user:kyc_verified:{}"


async def set_kyc_verified(client: aioredis.Redis, user_id: UUID) -> None:
    await client.set(_KYC_KEY.format(user_id), "1")


async def get_kyc_cache(client: aioredis.Redis, user_id: UUID) -> bool | None:
    """Return True if cached as verified, False if cached as not, None if no entry."""
    val = await client.get(_KYC_KEY.format(user_id))
    if val is None:
        return None
    return val == "1"