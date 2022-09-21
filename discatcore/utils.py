"""
The MIT License (MIT)

Copyright (c) 2022-present EmreTech

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

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


def _ensure_snowflake_is_int(sf: Snowflake) -> int:
    ret_id = sf
    if isinstance(ret_id, str):
        ret_id = int(ret_id)

    return ret_id


DISCORD_EPOCH = 1420070400000


class SnowflakeUtils:
    @staticmethod
    def snowflake_timestamp(id: Snowflake) -> int:
        """
        The timestamp stored in this object's Snowflake ID.

        Parameters
        ----------
        id: :type:`Snowflake`
            The snowflake to extract from
        """
        return (_ensure_snowflake_is_int(id) >> 22) + DISCORD_EPOCH

    @staticmethod
    def snowflake_iwid(id: Snowflake) -> int:
        """
        The internal worker ID stored in this object's
        Snowflake ID.

        Parameters
        ----------
        id: :type:`Snowflake`
            The snowflake to extract from
        """
        return (_ensure_snowflake_is_int(id) & 0x3E0000) >> 17

    @staticmethod
    def snowflake_ipid(id: Snowflake) -> int:
        """
        The internal process ID stored in this object's
        Snowflake ID.

        Parameters
        ----------
        id: :type:`Snowflake`
            The snowflake to extract from
        """
        return (_ensure_snowflake_is_int(id) & 0x1F000) >> 12

    @staticmethod
    def snowflake_increment(id: Snowflake) -> int:
        """
        The increment of the object's Snowflake ID.

        Parameters
        ----------
        id: :type:`Snowflake`
            The snowflake to extract from
        """
        return _ensure_snowflake_is_int(id) & 0xFFF


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
