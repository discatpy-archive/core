# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from discatcore.gateway.events.core import generate_handlers_from
from discatcore.gateway.events.event_protos import GatewayEventProtos

if TYPE_CHECKING:
    from discatcore.client import Client

__all__ = ("GatewayEventHandler",)


@generate_handlers_from(GatewayEventProtos)
class GatewayEventHandler:
    """Registers handlers that can convert raw Gateway event data into arguments."""

    def __init__(self, client: Client):
        self.client = client
