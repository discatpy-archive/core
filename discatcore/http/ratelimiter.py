# SPDX-License-Identifier: MIT

import logging
import typing as t
from datetime import datetime, timezone

from aiohttp import ClientResponse

from ..errors import BucketMigrated
from ..impl.ratelimit import BurstRatelimiter, ManualRatelimiter

_log = logging.getLogger(__name__)

__all__ = (
    "Bucket",
    "Ratelimiter",
)


class Bucket(BurstRatelimiter):
    """Represents a bucket in the Discord API.

    Attributes:
        reset (t.Optional[datetime.datetime]): The raw timestamp (processed into a datetime) when the bucket will reset.
            Defaults to None.
        bucket (t.Optional[str]): The hash denoting this bucket. This value is straight from the Discord API.
            Defaults to None.
    """

    __slots__ = (
        "reset",
        "bucket",
        "_first_update",
        "_migrated",
    )

    def __init__(self) -> None:
        BurstRatelimiter.__init__(self)

        self.reset: t.Optional[datetime] = None
        self.bucket: t.Optional[str] = None
        self._first_update: bool = True
        self._migrated: bool = False

    def update_info(self, response: ClientResponse) -> None:
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

    def migrate_to(self, discord_hash: str) -> t.NoReturn:
        """Migrates this bucket to a new one provided by the Discord API.

        Raises:
            BucketMigrated: An internal exception for the request function to change buckets.
        """
        self._migrated = True
        raise BucketMigrated(discord_hash)

    @property
    def migrated(self) -> bool:
        return self._migrated


class Ratelimiter:
    """Represents the global ratelimiter.

    Attributes:
        discord_buckets (dict[str, Bucket]): A mapping that maps Discord hashes to bucket objects.
        url_buckets (dict[str, Bucket]): A mapping that maps psuedo-buckets to bucket objects.
            This is primarily used by new requests that do not know their Discord hashes.
        url_to_discord_hash (dict[str, str]): A mapping that maps psuedo-buckets to Discord hashes.
            This is primarily set by requests that have just discovered their Discord hashes.
        global_bucket (ManualRatelimiter): The global bucket. Used for requests that involve global 429s.
    """

    __slots__ = ("discord_buckets", "url_buckets", "url_to_discord_hash", "global_bucket")

    def __init__(self) -> None:
        self.discord_buckets: dict[str, Bucket] = {}
        self.url_buckets: dict[str, Bucket] = {}
        self.url_to_discord_hash: dict[str, str] = {}
        self.global_bucket = ManualRatelimiter()

    def get_bucket(self, url: str) -> Bucket:
        """Gets a bucket object from the providing url.

        Args:
            url (str): The url to grab the bucket with.
                This can either be a pseudo-bucket or an actual Discord hash.
        """
        if url not in self.url_to_discord_hash:
            # this serves as a temporary bucket until further ratelimiting info is provided
            # or since some routes have no ratelimiting, they have to backfire to this bucket instead
            new_bucket = Bucket()
            self.url_buckets[url] = new_bucket
            return new_bucket

        discord_hash = self.url_to_discord_hash[url]
        return self.discord_buckets[discord_hash]

    def migrate_bucket(self, url: str, discord_hash: str) -> t.NoReturn:
        """Migrates a bucket object from a pseudo-bucket to a Discord hash.
        Not only will this call :meth:`Bucket.migrate_to`, but the mappings will be updated.

        Args:
            url (str): The pseudo-bucket of the bucket to migrate.
            discord_hash (str): The Discord hash to migrate the bucket to.
        """
        self.url_to_discord_hash[url] = discord_hash

        cur_bucket = self.url_buckets[url]
        self.discord_buckets[discord_hash] = cur_bucket
        del self.url_buckets[url]

        cur_bucket.migrate_to(discord_hash)
