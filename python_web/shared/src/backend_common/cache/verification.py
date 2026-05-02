"""Verification code generation and validation using Redis-backed caching.

Handles one-time code lifecycle including generation, cooldown enforcement,
attempt tracking, and secure verification.
"""

import secrets

from backend_common.cache.service import CacheService
from backend_common.exceptions import (
    CodeExpiredException,
    CooldownActiveException,
    InvalidCodeException,
    TooManyAttemptsException,
)


class VerificationCodeService:
    """Manages verification code generation, storage, and validation.

    Enforces cooldown periods between code requests and limits the number
    of failed verification attempts before locking out further tries.

    Attributes:
        cache: The underlying cache service for storing codes and metadata.
        code_ttl: How long a generated code remains valid, in seconds.
        cooldown_seconds: Minimum wait time between code generation requests.
        max_attempts: Maximum failed verification attempts before lockout.
    """

    def __init__(
        self,
        cache: CacheService,
        code_ttl: int = 300,
        cooldown_seconds: int = 120,
        max_attempts: int = 5,
    ) -> None:
        """Initialize the verification code service.

        Args:
            cache: The cache service for storing codes and state.
            code_ttl: Code validity duration in seconds.
            cooldown_seconds: Cooldown period between code requests in seconds.
            max_attempts: Maximum allowed failed verification attempts.
        """
        self.cache = cache
        self.code_ttl = code_ttl
        self.cooldown_seconds = cooldown_seconds
        self.max_attempts = max_attempts

    def _key(self, prefix: str, scope: str, identifier: str) -> str:
        return f"{prefix}:{scope}:{identifier}"

    async def generate_and_store(self, scope: str, identifier: str) -> str:
        """Generate a new 4-digit verification code and store it in cache.

        Args:
            scope: The verification context (e.g. "email", "phone").
            identifier: The target identifier (e.g. email address).

        Returns:
            The generated 4-digit code as a string.

        Raises:
            CooldownActiveException: When a code was recently generated for
                this scope and identifier.
        """
        cooldown_key = self._key("cooldown", scope, identifier)
        if await self.cache.exists(cooldown_key):
            raise CooldownActiveException()
        await self.cache.set(cooldown_key, "1", self.cooldown_seconds)

        code = f"{secrets.randbelow(9000) + 1000}"
        code_key = self._key("code", scope, identifier)
        await self.cache.set(code_key, code, self.code_ttl)
        return code

    async def verify(self, scope: str, identifier: str, code: str) -> bool:
        """Verify a code against the stored value.

        Args:
            scope: The verification context (e.g. "email", "phone").
            identifier: The target identifier (e.g. email address).
            code: The code provided by the user.

        Returns:
            True if the code matches.

        Raises:
            CodeExpiredException: When no code exists for this scope/identifier.
            InvalidCodeException: When the code does not match.
            TooManyAttemptsException: When the maximum attempts have been exceeded.
        """
        code_key = self._key("code", scope, identifier)
        attempts_key = self._key("attempts", scope, identifier)

        current = await self.cache.get(attempts_key)
        if current and int(current) >= self.max_attempts:
            await self.cache.delete(code_key)
            raise TooManyAttemptsException()

        stored_code = await self.cache.get(code_key)
        if not stored_code:
            raise CodeExpiredException()

        if stored_code != code:
            count = await self.cache.increment(attempts_key)
            if count == 1:
                await self.cache.expire(attempts_key, self.code_ttl)
            if count >= self.max_attempts:
                await self.cache.delete(code_key)
                raise TooManyAttemptsException()
            raise InvalidCodeException()

        await self.cache.delete(code_key)
        await self.cache.delete(attempts_key)
        return True