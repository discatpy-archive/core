# SPDX-License-Identifier: MIT

import typing as t
from datetime import datetime

has_orjson: bool = False
try:
    import orjson

    has_orjson = True
except ImportError:
    import json

__all__ = (
    "DISCORD_EPOCH",
    "Snowflake",
    "dumps",
    "loads",
)


DISCORD_EPOCH: t.Final[int] = 1420070400000


class Snowflake(int):
    @property
    def raw_timestamp(self) -> float:
        return ((self >> 22) + DISCORD_EPOCH) / 1000

    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.raw_timestamp)

    @property
    def internal_worker_id(self) -> int:
        return (self & 0x3E0000) >> 17

    @property
    def internal_process_id(self) -> int:
        return (self & 0x1F000) >> 12

    iwid = internal_worker_id
    ipid = internal_process_id

    @property
    def increment(self) -> int:
        return self & 0xFFF


def dumps(obj: t.Any) -> str:
    if has_orjson:
        return orjson.dumps(obj).decode("utf-8")
    return json.dumps(obj)


def loads(obj: str) -> t.Any:
    if has_orjson:
        return orjson.loads(obj)
    return json.loads(obj)
