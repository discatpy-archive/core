# SPDX-License-Identifier: MIT

import inspect
from collections import OrderedDict
from collections.abc import Callable
from datetime import datetime
from typing import TypeVar, get_args

from discatcore.types import Snowflake, Unset
from discatcore.utils import create_fn, from_import, indent_text

__all__ = ("generate_handlers_from",)

T = TypeVar("T")
_custom_type_handlers: OrderedDict[Callable[[type], bool], str] = OrderedDict(
    {
        (
            lambda t: t is datetime or datetime in get_args(t)
        ): 'datetime.fromisoformat(raw.get("{0.name}", ...)) if raw.get("{0.name}", ...) not in (..., None) else raw.get("{0.name}", ...)',
        (lambda _: True): 'cast({0.annotation}, raw.get("{0.name}", ...))',
    }
)


def _generate_body(args: list[inspect.Parameter]):
    ret_tuple = indent_text("return (")

    if len(args) == 1:
        ret_tuple += "cast({0.annotation}, raw), ".format(args[0])
    else:
        for arg in args:
            type_cast = ""
            for condition, tc in _custom_type_handlers.items():
                if condition(arg.annotation):
                    type_cast = tc + ", "

            ret_tuple += type_cast.format(arg)

    ret_tuple += ")"
    return [
        ret_tuple,
    ]


func_locals = {
    "Snowflake": Snowflake,
    "Unset": Unset,
}
from_import(
    "typing",
    func_locals,
    [
        "Any",
        "cast",
        "Dict",
        "List",
        "Optional",
        "Tuple",
        "Type",
        "Union",
    ],
)
from_import(
    "types",
    func_locals,
    [
        "NoneType",
    ],
)
from_import("discord_typings", func_locals)
from_import(
    "datetime",
    func_locals,
    [
        "datetime",
    ],
)


def generate_handlers_from(src_cls: type) -> Callable[[T], T]:
    def wrapper(cls: T):
        ignore_keys: list[str] = getattr(src_cls, "__ignore__", [])
        proto_keys = [k for k in dir(src_cls) if k not in ignore_keys and not k.startswith("_")]

        for k in proto_keys:
            proto = getattr(src_cls, k)
            sig = inspect.signature(proto)

            params = list(sig.parameters.values())
            params.pop(0)  # this should ALWAYS be the self parameter

            func_body = _generate_body(params)
            func = create_fn(f"handle_{k}", ["self", "raw: Any"], func_body, locals=func_locals)
            setattr(cls, f"handle_{k}", func)

        return cls

    return wrapper
