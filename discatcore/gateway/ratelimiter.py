# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .client import GatewayClient

__all__ = ("Ratelimiter",)

_log = logging.getLogger(__name__)


# TODO: refactor to incorporate the ratelimiting implementations in
# impl/ratelimit.py (for consistency)
class Ratelimiter:
    """Represents a ratelimiter for a Gateway Client."""

    __slots__ = (
        "commands_used",
        "parent",
        "_task",
        "_ratelimit_done",
        "_lock",
        "limit",
        "reset_after",
    )

    def __init__(self, parent: GatewayClient, limit: int = 120, reset_after: int = 60):
        self.commands_used = 0
        self.limit = limit
        self.reset_after = reset_after
        self.parent = parent
        self._task: Optional[asyncio.Task[Any]] = None
        self._ratelimit_done = asyncio.Event()
        self._lock = asyncio.Event()

    async def ratelimit_loop(self):
        """Updates the amount of commands used per minute."""
        while not self.parent.is_closed:
            try:
                self._ratelimit_done.clear()

                await asyncio.sleep(self.reset_after)

                self._ratelimit_done.set()
                self.commands_used = 0
            except asyncio.CancelledError:
                break

    def start(self):
        """Starts the ratelimiter task which updates the commands used per minute."""
        if not self._task:
            self._task = asyncio.create_task(self.ratelimit_loop())
            _log.info("Started Gateway ratelimiting task.")

    async def stop(self):
        """Stops the ratelimiter task."""
        if self._task:
            self._task.cancel()
            await self._task
            _log.info("Stopped Gateway ratelimiting task.")

    def add_command_usage(self):
        self.commands_used += 1
        _log.debug("A Gateway command has been used.")

    def is_ratelimited(self):
        return self.commands_used == self.limit - 1

    async def acquire(self):
        """Waits for the lock to be unlocked."""
        if not self.is_ratelimited():
            return

        start_time = datetime.now()
        _log.info("Waiting for the Gateway ratelimit lock.")

        await self._ratelimit_done.wait()

        end_time = datetime.now()
        _log.info(
            "Done waiting for the Gateway ratelimit lock! It took %f seconds.",
            (end_time - start_time).total_seconds(),
        )

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, *args: Any):
        pass
