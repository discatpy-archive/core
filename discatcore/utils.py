# SPDX-License-Identifier: MIT

import builtins
import importlib
import types
from collections.abc import Callable, Coroutine
from typing import Any, Optional, Union

from discatcore.types import Snowflake

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
    "indent_text",
    "indent_all_text",
    "create_fn",
    "from_import",
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


Func = Callable[..., Any]
CoroFunc = Callable[..., Coroutine[Any, Any, Any]]


def indent_text(txt: str, *, num_spaces: int = 4) -> str:
    return " " * num_spaces + txt


def indent_all_text(strs: list[str]) -> list[str]:
    output: list[str] = []

    for txt in strs:
        output.append(indent_text(txt))

    return output


# Code taken from the dataclasses module in the Python stdlib
def create_fn(
    name: str,
    args: list[str],
    body: list[str],
    *,
    globals: Optional[dict[str, Any]] = None,
    locals: Optional[dict[str, Any]] = None,
    return_type: type = ...,
    asynchronous: bool = False,
) -> Union[CoroFunc, Func]:
    if locals is None:
        locals = {}

    if "BUILTINS" not in locals:
        locals["BUILTINS"] = builtins

    return_annotation = ""
    if return_type is not ...:
        locals["_return_type"] = return_type
        return_annotation = "-> _return_type"

    fargs = ", ".join(args)
    fbody = "\n".join(indent_all_text(body))

    # Compute the text of the entire function.
    txt = ""
    if asynchronous:
        txt += "async "
    txt += f"def {name}({fargs}) {return_annotation}:\n{fbody}"

    local_vars = ", ".join(locals.keys())
    txt = f"def __create_fn__({local_vars}):\n{indent_text(txt)}\n    return {name}"
    ns = {}
    exec(txt, globals, ns)

    # there's no good way to explicity inform pyright the return of this
    # it is a static type checker after all
    return ns["__create_fn__"](**locals)  # type: ignore


def _get_everything_from_module(mod: types.ModuleType):
    everything: dict[str, Any] = {}
    keys = [k for k in dir(mod) if not k.startswith("_")]

    for k in keys:
        everything[k] = getattr(mod, k)
        if isinstance(everything[k], types.ModuleType):
            everything.update(_get_everything_from_module(everything[k]))

    return everything


def from_import(module: str, locals: dict[str, Any], objs_to_grab: Optional[list[str]] = None):
    actual_module = importlib.import_module(module)

    if objs_to_grab:
        for obj in objs_to_grab:
            v = getattr(actual_module, obj)
            locals[obj] = v
    else:
        locals.update(_get_everything_from_module(actual_module))
