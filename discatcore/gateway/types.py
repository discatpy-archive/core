# SPDX-License-Identifier: MIT

import typing as t
from dataclasses import dataclass

import aiohttp
from typing_extensions import TypeGuard

DT = t.TypeVar("DT")

__all__ = (
    "BaseTypedWSMessage",
    "TextTypedWSMessage",
    "BinaryTypedWSMessage",
    "is_text",
    "is_binary",
    "convert_from_untyped",
)


@dataclass
class BaseTypedWSMessage(t.Generic[DT]):
    type: aiohttp.WSMsgType
    data: DT
    extra: str

    @classmethod
    def convert_from_untyped(cls, msg: aiohttp.WSMessage):
        return cls(
            t.cast(aiohttp.WSMsgType, msg[0]),
            t.cast(DT, msg[1]),
            t.cast(str, msg[2]),
        )


TextTypedWSMessage = BaseTypedWSMessage[str]
BinaryTypedWSMessage = BaseTypedWSMessage[bytes]


def is_text(base: BaseTypedWSMessage[t.Any]) -> TypeGuard[TextTypedWSMessage]:
    return base.type is aiohttp.WSMsgType.TEXT


def is_binary(base: BaseTypedWSMessage[t.Any]) -> TypeGuard[BinaryTypedWSMessage]:
    return base.type is aiohttp.WSMsgType.BINARY


def convert_from_untyped(msg: aiohttp.WSMessage):
    base: BaseTypedWSMessage[t.Any] = BaseTypedWSMessage.convert_from_untyped(msg)

    if base.type == aiohttp.WSMsgType.TEXT:
        return t.cast(TextTypedWSMessage, base)
    elif base.type == aiohttp.WSMsgType.BINARY:
        return t.cast(BinaryTypedWSMessage, base)
    return base
