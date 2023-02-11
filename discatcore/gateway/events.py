# SPDX-License-Identifier: MIT
from __future__ import annotations

import typing as t
from dataclasses import dataclass

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


@dataclass
class GatewayEvent(Event):
    pass


@dataclass
class DispatchEvent(GatewayEvent):
    data: t.Mapping[str, t.Any]


@dataclass
class ReadyEvent(GatewayEvent):
    data: dt.ReadyData


@dataclass
class ResumedEvent(GatewayEvent):
    pass


@dataclass
class ReconnectEvent(GatewayEvent):
    pass


@dataclass
class InvalidSessionEvent(GatewayEvent):
    resumable: bool
