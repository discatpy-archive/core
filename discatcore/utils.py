# SPDX-License-Identifier: MIT

from typing import Any

from .types import Snowflake

has_orjson = False
try:
    import orjson

    has_orjson = True
except ImportError:
    import json

__all__ = (
    "DISCORD_EPOCH",
    "SnowflakeUtils",
    "dumps",
    "loads",
)


DISCORD_EPOCH = 1420070400000


class SnowflakeUtils:
    """Utilities for handling Snowflakes."""

    @staticmethod
    def snowflake_timestamp(id: Snowflake) -> int:
        """The timestamp of the provided Snowflake.

        Args:
            id (Snowflake): The snowflake to extract from.
        """
        return (int(id) >> 22) + DISCORD_EPOCH

    @staticmethod
    def snowflake_iwid(id: Snowflake) -> int:
        """The internal worker ID of the provided Snowflake.

        Args:
            id (Snowflake): The snowflake to extract from.
        """
        return (int(id) & 0x3E0000) >> 17

    @staticmethod
    def snowflake_ipid(id: Snowflake) -> int:
        """The internal process ID of the provided Snowflake.

        Args:
            id (Snowflake): The snowflake to extract from.
        """
        return (int(id) & 0x1F000) >> 12

    @staticmethod
    def snowflake_increment(id: Snowflake) -> int:
        """The increment of the provided Snowflake.

        Args:
            id (Snowflake): The snowflake to extract from.
        """
        return int(id) & 0xFFF


def dumps(obj: Any):
    if has_orjson:
        return orjson.dumps(obj).decode("utf-8")
    return json.dumps(obj)


def loads(obj: str):
    if has_orjson:
        return orjson.loads(obj)
    return json.loads(obj)
