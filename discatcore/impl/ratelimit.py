"""
The MIT License (MIT)

Copyright (c) 2022-present EmreTech

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import asyncio
from typing import Optional

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

    async def __aexit__(self, *args):
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
