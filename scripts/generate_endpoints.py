import argparse
import builtins
import contextlib
import dataclasses
import json
import pathlib
import types
from typing import Any, Optional, overload, Union, TypeVar

import discord_typings

#
#  Constants
#

DEFAULT_SOURCE_DIR = "data/endpoints"
DEFAULT_DEST_DIR = "discatcore/http/endpoints"
VALID_METHODS = ["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"]
T = TypeVar("T")


class _UnsetDefine:
    pass


_Unset = _UnsetDefine()

#
#  Function Creator
#

# taken from typing
# https://github.com/python/cpython/blob/3.10/Lib/typing.py#L185-L203
def _type_repr(obj):
    """Return the repr() of an object, special-casing types (internal helper).
    If obj is a type, we return a shorter version than the default
    type.__repr__, based on the module and qualified name, which is
    typically enough to uniquely identify a type.  For everything
    else, we fall back on repr(obj).
    """
    if isinstance(obj, types.GenericAlias):
        return repr(obj)
    if isinstance(obj, type):
        if obj.__module__ == "builtins":
            return obj.__qualname__
        return f"{obj.__module__}.{obj.__qualname__}"
    if obj is ...:
        return "..."
    if isinstance(obj, types.FunctionType):
        return obj.__name__
    return repr(obj)


@dataclasses.dataclass
class FunctionArg:
    name: Optional[str] = None
    _: dataclasses.KW_ONLY
    annotation: Union[str, types.EllipsisType] = ...
    default: Any = _Unset
    pos_and_kw: bool = True
    pos_modifier: bool = False
    kw_modifier: bool = False
    variable_pos: bool = False
    variable_kw: bool = False

    def __post_init__(self):
        if self.pos_modifier and self.kw_modifier:
            raise ValueError(
                f"arg {self.name} cannot be both a positional modifier and a keyword modifier!"
            )
        if self.variable_pos and self.variable_kw:
            raise ValueError(
                f"arg {self.name} cannot be both a variable positional argument and a variable keyword argument!"
            )
        if (self.pos_modifier or self.kw_modifier) and (self.variable_pos or self.variable_kw):
            raise ValueError(f"arg {self.name} cannot be both a modifier and a variable argument!")
        if (self.pos_modifier or self.kw_modifier) and self.name:
            raise ValueError(f"arg {self.name} cannot be a modifier and have a name!")
        elif not (self.pos_modifier or self.kw_modifier) and not self.name:
            raise ValueError(f"non-modifier args require a name!")
        if (self.pos_modifier or self.kw_modifier) and self.annotation is not ...:
            raise ValueError(f"modifier args cannot have annotations!")


def indent(text: str, *, level: int = 1):
    return "    " * level + text


class FunctionCreator:
    """A class that can dynamically create a function in a nice, OOP styled fashion.

    Args:
        name (str): The name of this function.
        decorators (Optional[List[:class:`str`]]): The list of decorators for this function. Defaults to None.
        is_async (bool): Whether or not this function is asynchronous. Defaults to False.

    Attributes:
        func_args (List[:class:`FunctionArg`]): The list of arguments for this function.
    """

    def __init__(
        self, name: str, *, decorators: Optional[list[str]] = None, is_async: bool = False
    ):
        self.func_name: str = name
        self.func_async: bool = is_async
        self.func_args: list[FunctionArg] = []
        self.func_return_anno: Union[str, types.EllipsisType] = ...
        self.func_decorators: Optional[list[str]] = decorators
        self.func_body: list[str] = []
        self.func_indent_level: int = 1

    def insert_arg(self, arg: FunctionArg, index: int):
        self.func_args.insert(index, arg)

    def append_arg(self, arg: FunctionArg):
        self.func_args.append(arg)

    def remove_arg(self, index: int):
        del self.func_args[index]

    @contextlib.contextmanager
    def indent(self):
        self.func_indent_level += 1
        try:
            yield
        finally:
            self.func_indent_level -= 1

    def print(self, *args):
        if not args:
            self.func_body.append("")
        else:
            self.func_body.extend([indent(arg, level=self.func_indent_level) for arg in args])

    def print_block(self, lines: str):
        for line in lines.splitlines():
            self.print(line)

    def _convert_arg_to_str(self, arg: FunctionArg):
        str_arg: str = ""

        if (arg.variable_pos or arg.variable_kw or arg.pos_and_kw) and arg.name:
            if arg.variable_pos or arg.variable_kw:
                str_arg += "*" * (arg.variable_pos or arg.variable_kw * 2)
            str_arg += arg.name

            if arg.annotation is not ...:
                str_arg += f": {arg.annotation}"
            if arg.default is not _Unset:
                str_arg += f" = {arg.default}"
        else:
            str_arg += "*" if arg.kw_modifier else "/"

        return str_arg

    def generate_raw(self):
        func_str = ""
        if self.func_async:
            func_str += "async "

        str_args = ", ".join([self._convert_arg_to_str(arg) for arg in self.func_args])
        func_str += f"def {self.func_name}({str_args})"
        if self.func_return_anno is not ...:
            func_str += f" -> {self.func_return_anno}"
        func_str += ":\n" + "\n".join(self.func_body)

        return func_str

    def generate(self, *, globals: dict[str, Any] = {}, locals: dict[str, Any] = {}) -> types.FunctionType:
        if "BUILTINS" not in locals:
            locals["BUILTINS"] = builtins

        func_str = "\n".join(
            [indent(line) for line in self.generate_raw().splitlines()]
        )
        local_vars = ", ".join(locals.keys())
        func_creator_str = (
            f"def __create_fn__({local_vars}):\n{func_str}\n    return {self.func_name}"
        )

        ns = {}
        exec(func_creator_str, globals, ns)

        func = ns["__create_fn__"](**locals)
        if not isinstance(func, types.FunctionType):
            raise TypeError(f"the generated object was of type {type(func)!r}, not types.FunctionType!")
        return func


#
#  JSON Parsing
#

func_globals = {
    "Snowflake": discord_typings.Snowflake,
    "discord_typings": discord_typings,
    "ellipsis": types.EllipsisType,
    "Union": Union,
}


@overload
def _dict_type_check(d: dict[Any, Any], key: Any, expected_type: type[T]) -> T:
    ...


@overload
def _dict_type_check(
    d: dict[Any, Any], key: Any, expected_type: type[T], *, is_required: bool = ...
) -> Union[T, _UnsetDefine]:
    ...


def _dict_type_check(
    d: dict[Any, Any], key: Any, expected_type: type[T], *, is_required: bool = True
) -> Union[T, _UnsetDefine]:
    val = d.get(key, ...)
    if val is ... and is_required:
        raise KeyError(key)
    elif val is ...:
        return _Unset

    if isinstance(val, expected_type):
        return val
    raise TypeError(f"the value at key {key} is not of type {_type_repr(expected_type)}!")


def _generate_func_args_json_query(
    func_gen: FunctionCreator,
    params: dict[Any, Any],
):
    for param_name, param in params.items():
        default = _Unset
        if isinstance(param, str):
            anno = param
        elif isinstance(param, list) and len(param) == 2:
            anno, default = param
        else:
            raise TypeError(
                f"Invalid type {_type_repr(param)} for JSON/Query parameter values"
            )

        func_gen.append_arg(FunctionArg(param_name, annotation=anno, default=default))


def _generate_func_args(
    func_gen: FunctionCreator,
    url_params: Union[dict[Any, Any], _UnsetDefine],
    json_params: Union[dict[Any, Any], _UnsetDefine],
    query_params: Union[dict[Any, Any], _UnsetDefine],
):
    # I know that if x is not _Unset should be used but Pyright does not really seem to
    # support singletons well (except for None) so whenever I type a parameter _UnsetDefine
    # then Pyright thinks that _Unset could be assigned or any other instance of _UnsetDefine.
    # This behavior is annoying and I hope the Pyright team changes it (if they can).

    if not isinstance(url_params, _UnsetDefine):
        for param_name, param_anno in url_params.items():
            func_gen.append_arg(FunctionArg(param_name, annotation=param_anno))

    if not isinstance(json_params, _UnsetDefine) or not isinstance(query_params, _UnsetDefine):
        func_gen.append_arg(FunctionArg(kw_modifier=True))

        if not isinstance(json_params, _UnsetDefine) and not isinstance(query_params, _UnsetDefine): # rare case
            _generate_func_args_json_query(func_gen, json_params)
            _generate_func_args_json_query(func_gen, query_params)
        else:
            # Pyright cannot infer that because of the protection of the first if statement 
            # (not the one this else is the opposite of but the other one) query_params cannot be
            # an instance of _UnsetDefine.
            _generate_func_args_json_query(func_gen, json_params if not isinstance(json_params, _UnsetDefine) else query_params)  # type: ignore


def parse_endpoint_func(name: str, func: dict[str, Any]):
    method = _dict_type_check(func, "method", str)
    url = _dict_type_check(func, "url", str)
    url_params = _dict_type_check(func, "url-parameters", dict, is_required=False)
    json_params = _dict_type_check(func, "json-parameters", dict, is_required=False)
    query_params = _dict_type_check(func, "query-parameters", dict, is_required=False)

    func_generator = FunctionCreator(name, is_async=True)

    # generate arguments
    func_generator.append_arg(FunctionArg("self"))
    _generate_func_args(func_generator, url_params, json_params, query_params)

    # TODO: generate body

    return func_generator.generate(globals=func_globals)


#
#  Main
#


def is_path_legit(p: pathlib.Path):
    return p.exists() and p.is_dir()


def parse_args():
    parser = argparse.ArgumentParser(
        prog="generate_endpoints",
        description="A helper for DisCatCore that processes JSON files into HTTP Endpoint functions.",
    )

    parser.add_argument(
        "-s",
        "--source",
        default=DEFAULT_SOURCE_DIR,
        help="The source directory where the JSON files are located.",
    )
    parser.add_argument(
        "-d",
        "--destination",
        default=DEFAULT_DEST_DIR,
        help="The destination directory where the generated Python files will be stored.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Whether or not the generated files should be stored. This will print the file's contents to STDOUT.",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    src_dir = pathlib.Path(args.source)
    dest_dir = pathlib.Path(args.destination)

    if not is_path_legit(src_dir):
        raise ValueError(
            f"Source path {str(src_dir)} is not valid. Please retry with a valid path."
        )
    if not is_path_legit(dest_dir):
        raise ValueError(
            f"Destination path {str(dest_dir)} is not valid. Please retry with a valid path."
        )

    for file in src_dir.glob("*.json"):
        print(str(file) + ":")
        print(json.loads(file.read_text()))


if __name__ == "__main__":
    main()
