# SPDX-License-Identifier: MIT

import asyncio
from typing import Any, Optional

__all__ = (
    "BaseRatelimiter",
    "ManualRatelimiter",
    "BurstRatelimiter",
)


class BaseRatelimiter:
    __slots__ = ("_lock",)

    def __init__(self):
        self._lock = asyncio.Event()
        self._lock.set()

    async def acquire(self):
        await self._lock.wait()

    async def _unlock(self, delay: float):
        await asyncio.sleep(delay)
        self._lock.set()

    def lock_for(self, delay: float):
        """Locks the bucket for a given amount of time.

        Args:
            delay (float): How long the bucket should be locked for.
        """
        if self.is_locked():
            return

        self._lock.clear()
        asyncio.create_task(self._unlock(delay))

    def is_locked(self):
        """:bool: Returns whether the bucket is locked or not."""
        return not self._lock.is_set()

    async def __aenter__(self):
        await self.acquire()
        return None

    async def __aexit__(self, *args: Any):
        pass


class ManualRatelimiter(BaseRatelimiter):
    pass


class BurstRatelimiter(BaseRatelimiter):
    __slots__ = ("limit", "remaining", "reset_after")

    def __init__(self):
        BaseRatelimiter.__init__(self)

        self.limit: Optional[int] = None
        self.remaining: Optional[int] = None
        self.reset_after: Optional[float] = None

    async def acquire(self):
        if self.reset_after is not None and self.remaining == 0 and not self.is_locked():
            self.lock_for(self.reset_after)

        return await super().acquire()
