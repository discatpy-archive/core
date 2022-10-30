# SPDX-License-Identifier: MIT

import typing as t

import discord_typings as dt

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
    def snowflake_timestamp(id: dt.Snowflake) -> int:
        """The timestamp of the provided Snowflake.

        Args:
            id (Snowflake): The snowflake to extract from.
        """
        return (int(id) >> 22) + DISCORD_EPOCH

    @staticmethod
    def snowflake_iwid(id: dt.Snowflake) -> int:
        """The internal worker ID of the provided Snowflake.

        Args:
            id (Snowflake): The snowflake to extract from.
        """
        return (int(id) & 0x3E0000) >> 17

    @staticmethod
    def snowflake_ipid(id: dt.Snowflake) -> int:
        """The internal process ID of the provided Snowflake.

        Args:
            id (Snowflake): The snowflake to extract from.
        """
        return (int(id) & 0x1F000) >> 12

    @staticmethod
    def snowflake_increment(id: dt.Snowflake) -> int:
        """The increment of the provided Snowflake.

        Args:
            id (Snowflake): The snowflake to extract from.
        """
        return int(id) & 0xFFF


def dumps(obj: t.Any):
    if has_orjson:
        return orjson.dumps(obj).decode("utf-8")
    return json.dumps(obj)


def loads(obj: str):
    if has_orjson:
        return orjson.loads(obj)
    return json.loads(obj)
