# SPDX-License-Identifier: MIT
from __future__ import annotations

import typing as t

import attr
import discord_typings as dt

from ..utils.event import Event

__all__ = (
    "GatewayEvent",
    "DispatchEvent",
    "InvalidSessionEvent",
    "ReadyEvent",
    "ReconnectEvent",
    "ResumedEvent",
)


@attr.define
class GatewayEvent(Event):
    pass


@attr.define
class DispatchEvent(GatewayEvent):
    data: t.Mapping[str, t.Any]


@attr.define
class ReadyEvent(GatewayEvent):
    data: dt.ReadyData


@attr.define
class ResumedEvent(GatewayEvent):
    pass


@attr.define
class ReconnectEvent(GatewayEvent):
    pass


@attr.define
class InvalidSessionEvent(GatewayEvent):
    resumable: bool
