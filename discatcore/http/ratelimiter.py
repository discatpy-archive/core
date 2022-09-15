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
import logging
from datetime import datetime, timezone
from typing import Optional

from aiohttp import ClientResponse

from discatcore.errors import BucketMigrated

_log = logging.getLogger(__name__)

__all__ = (
    "Bucket",
    "GlobalBucket",
    "Ratelimiter",
)


# TODO: abstract out this ratelimiting logic
class Bucket:
    """Represents a ratelimiting bucket."""

    __slots__ = (
        "_lock",
        "limit",
        "remaining",
        "reset",
        "reset_after",
        "bucket",
        "_first_update",
        "_migrated",
    )

    def __init__(self):
        self.limit: Optional[int] = None
        self.remaining: Optional[int] = None
        self.reset: Optional[datetime] = None
        self.reset_after: Optional[float] = None
        self.bucket: Optional[str] = None

        self._first_update: bool = True
        self._migrated: bool = False
        self._lock = asyncio.Event()
        self._lock.set()

    def update_info(self, response: ClientResponse):
        """Updates the bucket's underlying information via the new headers.

        Args:
            response (aiohttp.ClientResponse): The response to update the bucket information with.
        """
        self.limit = int(response.headers.get("X-RateLimit-Limit", 1))
        raw_remaining = response.headers.get("X-RateLimit-Remaining")

        if response.status == 429:
            self.remaining = 0
        elif raw_remaining is None:
            self.remaining = 1
        else:
            converted_remaining = int(raw_remaining)

            if self._first_update:
                self.remaining = converted_remaining
            elif self.remaining is not None:
                self.remaining = (
                    converted_remaining if converted_remaining < self.remaining else self.remaining
                )

        raw_reset = response.headers.get("X-RateLimit-Reset")
        if raw_reset is not None:
            self.reset = datetime.fromtimestamp(float(raw_reset), timezone.utc)

        raw_reset_after = response.headers.get("X-RateLimit-Reset-After")
        if raw_reset_after is not None:
            raw_reset_after = float(raw_reset_after)

            if self.reset_after is None:
                self.reset_after = raw_reset_after
            else:
                self.reset_after = (
                    raw_reset_after if self.reset_after < raw_reset_after else self.reset_after
                )

        raw_bucket = response.headers.get("X-RateLimit-Bucket")
        self.bucket = raw_bucket

        if self._first_update:
            self._first_update = False

        if self.reset_after is not None and self.remaining == 0 and not self.is_locked():
            self.lock_for(self.reset_after)

    async def acquire(self):
        """Waits for bucket to be available. This will lock the bucket if needed."""
        if self.reset_after is not None and self.remaining == 0 and not self.is_locked():
            self.lock_for(self.reset_after)

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

    def migrate_to(self, discord_hash: str):
        self._migrated = True
        raise BucketMigrated(discord_hash)

    @property
    def migrated(self):
        return self._migrated

    async def __aenter__(self):
        await self.acquire()
        return None

    async def __aexit__(self, *args):
        pass


class GlobalBucket(Bucket):
    def update_info(self):
        # ensure that nothing calls this function
        pass

    async def acquire(self):
        await self._lock.wait()


class Ratelimiter:
    """Represents the global ratelimiter."""

    __slots__ = ("discord_buckets", "url_buckets", "url_to_discord_hash", "global_bucket")

    def __init__(self):
        self.discord_buckets: dict[str, Bucket] = {}
        self.url_buckets: dict[str, Bucket] = {}
        self.url_to_discord_hash: dict[str, str] = {}
        self.global_bucket = GlobalBucket()

    def get_bucket(self, url: str):
        if url not in self.url_to_discord_hash:
            # this serves as a temporary bucket until further ratelimiting info is provided
            # or since some routes have no ratelimiting, they have to backfire to this bucket instead
            new_bucket = Bucket()
            self.url_buckets[url] = new_bucket
            return new_bucket

        discord_hash = self.url_to_discord_hash[url]
        return self.discord_buckets[discord_hash]

    def migrate_bucket(self, url: str, discord_hash: str):
        self.url_to_discord_hash[url] = discord_hash

        cur_bucket = self.url_buckets[url]
        self.discord_buckets[discord_hash] = cur_bucket
        del self.url_buckets[url]

        cur_bucket.migrate_to(discord_hash)
