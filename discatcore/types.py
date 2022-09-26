# SPDX-License-Identifier: MIT

from typing import Any, NoReturn

from discord_typings import Snowflake

__all__ = (
    "Snowflake",
    "Unset",
)


class _UnsetDefine:
    __slots__ = ()
    __name__ = "Unset"

    def __eq__(self, other: Any) -> NoReturn:
        raise NotImplementedError("You cannot compare unset")

    def __repr__(self):
        return self.__class__.__name__

    __str__ = __repr__

    def __bool__(self) -> NoReturn:
        raise NotImplementedError("Unset is not set, it is not True, False, or None.")


Unset: Any = _UnsetDefine()
