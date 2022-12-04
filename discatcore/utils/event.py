# SPDX-License-Identifier: MIT

from __future__ import annotations

import typing as t
from dataclasses import dataclass

from typing_extensions import Self

if t.TYPE_CHECKING:
    from .dispatcher import ListenerCallback

__all__ = ("Event", "ExceptionEvent")

T = t.TypeVar("T")
EventT = t.TypeVar("EventT", bound="Event")


class _classproperty(t.Generic[T]):
    def __init__(self, fget: t.Callable[[t.Any], T], /) -> None:
        self.fget: "classmethod[T]" = t.cast("classmethod[T]", fget)

    def getter(self, fget: t.Callable[[t.Any], T], /) -> Self:
        self.fget = t.cast("classmethod[T]", fget)
        return self

    def __get__(self, obj: t.Optional[t.Any], type: t.Optional[type]) -> T:
        return self.fget.__func__(type)


class Event:
    """Represents a dispatcher event. An event class contains information about an event for use in listeners."""

    __slots__ = ()

    __dispatches: tuple[type[Event], ...]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        cls.__dispatches = tuple(base for base in cls.__mro__ if issubclass(base, Event))

    @_classproperty
    @classmethod
    def dispatches(cls):
        return cls.__dispatches


@dataclass(kw_only=True)
class ExceptionEvent(Event, t.Generic[EventT]):
    """An event that is dispatched whenever a dispatched event raises an exception."""

    exception: BaseException
    failed_event: EventT
    failed_listener: ListenerCallback[EventT]
