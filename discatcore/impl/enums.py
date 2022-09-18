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
from __future__ import annotations

import types
from collections.abc import Iterator, Sequence
from typing import Any, ClassVar, Union

__all__ = (
    "EnumMeta",
    "Enum",
)


def _is_descriptor(o: object) -> bool:
    return hasattr(o, "__set__") or hasattr(o, "__get__") or hasattr(o, "__delete__")


class _EnumDict(dict[str, Any]):
    __slots__ = ("bases", "members")

    def __init__(self, bases: tuple[type]):
        self.bases: tuple[type] = bases
        self.members: dict[str, Any] = {}

    def __setitem__(self, key: str, value: Any) -> None:
        if key.startswith("_") or _is_descriptor(value):
            return super().__setitem__(key, value)

        if not isinstance(value, self.bases):
            raise TypeError(f"Enum member {key} is not of type(s) {self.bases!r}!")

        if key in self.members:
            raise TypeError(f"Enum member {key} has already been set!")

        self.members[key] = value


def _get_public_keys(d: dict[str, Any]) -> Sequence[str]:
    return [k for k in d.keys() if k not in ("__dict__", "__module__", "__name__", "__qualname__")]


class _EnumMember:
    def __init__(self, enum_cls: EnumMeta, name: str, value: Any):
        orig_enum_keys = set(_get_public_keys(vars(Enum)))
        enum_dict_keys = set(_get_public_keys(enum_cls.__original_ns__))
        for key in enum_dict_keys - orig_enum_keys:
            setattr(self, key, enum_cls.__original_ns__[key])

        self._name_ = name
        self._value_ = value


def _create_member_cls(value_type: type) -> object:
    ns = {k: Enum.__dict__[k] for k in _get_public_keys(Enum.__dict__)}
    return type(f"{value_type.__name__}", (value_type, _EnumMember), ns)


def _reverse_dict(d: dict[Any, Any]) -> dict[Any, Any]:
    return {v: k for k, v in d.items()}


IS_ENUM_CREATED: bool = False


class EnumMeta(type):
    __base_types__: tuple[type]
    __member_map__: dict[str, object]
    __original_ns__: _EnumDict
    __member_classes__: ClassVar[dict[type, object]] = {}

    @classmethod
    def __prepare__(cls, name: str, bases: tuple[type, ...], **kwargs: Any) -> _EnumDict:
        if not IS_ENUM_CREATED:
            return _EnumDict((object,))

        member_bases = tuple(filter(lambda i: not issubclass(i, Enum), bases))
        return _EnumDict(member_bases)

    def __new__(cls, name: str, bases: tuple[type, ...], ns: _EnumDict, **kwargs: Any):
        global IS_ENUM_CREATED
        if not IS_ENUM_CREATED:
            IS_ENUM_CREATED = True
            return super().__new__(cls, name, bases, ns, **kwargs)

        new_ns = {
            "__base_types__": ns.bases,
            "__member_map__": (member_map := {}),
            "__original_ns__": ns,
        }
        new_ns.update(ns)
        ns.update(
            {
                k: v
                for k, v in Enum.__dict__.items()
                if k not in ("__dict__", "__module__", "__name__", "__qualname__")
            }
        )

        enum_mixins = tuple(filter(lambda i: issubclass(i, Enum), bases))
        new_cls = super().__new__(cls, name, enum_mixins, new_ns, **kwargs)

        for m_name, m_value in ns.members.items():
            if type(m_value) not in cls.__member_classes__:
                member_cls = _create_member_cls(type(m_value))
                cls.__member_classes__[type(m_value)] = member_cls
            else:
                member_cls = cls.__member_classes__[type(m_value)]

            member = type(m_value).__new__(member_cls, m_value)
            member.__init__(new_cls, m_name, m_value)

            member_map[m_name] = member
            setattr(new_cls, m_name, member)

        return new_cls

    def __repr__(cls) -> str:
        return f"<enum {cls.__name__}>"

    def __call__(cls, value: Any) -> str:
        try:
            return _reverse_dict(cls.__original_ns__.members)[value]
        except KeyError:
            raise ValueError(f"There is no enum member with the value {value!r}!") from None

    def __getitem__(cls, name: str) -> object:
        return cls.__member_map__[name]

    def __contains__(cls, value: Union[object, Any]) -> bool:
        return value in cls.__member_map__.values() or value in cls.__original_ns__.members.values()

    def __iter__(cls) -> Iterator[object]:
        yield from cls.__member_map__.values()

    def __len__(cls) -> int:
        return len(cls.__member_map__)

    @property
    def member_map(cls):
        return types.MappingProxyType(cls.__member_map__)


class Enum(metaclass=EnumMeta):
    __base_types__: ClassVar[tuple[type]]
    __member_map__: ClassVar[dict[str, object]]
    __original_ns__: ClassVar[_EnumDict]
    _name_: str
    _value_: Any

    @property
    def name(self):
        return self._name_

    @property
    def value(self):
        return self._value_
