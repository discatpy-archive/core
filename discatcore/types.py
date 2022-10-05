# SPDX-License-Identifier: MIT

from enum import Enum, auto
from typing import Literal, TypeVar, Union

from discord_typings import Snowflake

__all__ = (
    "Snowflake",
    "Unset",
    "UnsetOr",
)


class _UnsetEnum(Enum):
    Unset = auto()

    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "Unset"

    __str__ = __repr__


T = TypeVar("T")
Unset: Literal[_UnsetEnum.Unset] = _UnsetEnum.Unset
UnsetOr = Union[T, _UnsetEnum]
