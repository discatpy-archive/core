# SPDX-License-Identifier: MIT

import asyncio
import inspect
import logging
import traceback
from collections.abc import Callable, Coroutine
from typing import Any, Optional, TypeVar

from .event import Event

_log = logging.getLogger(__name__)

__all__ = ("Dispatcher",)

T = TypeVar("T")
Func = Callable[..., T]
CoroFunc = Func[Coroutine[Any, Any, Any]]


class Dispatcher:
    """A class that helps manage events.

    Attributes:
        events (dict[str, Event]): The callbacks for each event.
    """

    __slots__ = ("events",)

    def __init__(self) -> None:
        self.events: dict[str, Event] = {}

    def get_event(self, name: str) -> Optional[Event]:
        """Returns an event with the name provided.

        Args:
            name (str): The name of the event that will be returned.

        Returns:
            The event, none if not found.
        """
        return self.events.get(name)

    def new_event(self, name: str) -> Event:
        """Creates a new event. Returns this new event after creation.

        Args:
            name (str): The name of the new event.

        Returns:
            The new event created.
        """
        if name in self.events:
            return self.events[name]

        new_event = Event(name, self)
        self.events[name] = new_event
        return new_event

    def add_event(self, event: Event) -> None:
        """Adds a new pre-existing event.

        Args:
            event (Event): The event to add.
        """
        self.events[event.name] = event

    def remove_event(self, name: str) -> None:
        """Removes an event.

        Args:
            name (str): The name of the event to remove.
        """
        if name not in self.events:
            raise ValueError(f"There is no event with name {name}!")

        del self.events[name]
        _log.debug("Removed event with name %s", name)

    def has_event(self, name: str) -> bool:
        """Check if this dispatcher already has a event.

        Args:
            name (str): The name of the event to find.

        Returns:
            A bool correlating to if there is a event with that name or not.
        """
        return name in self.events

    # global error handler

    async def error_handler(self, exception: Exception) -> None:
        """Basic error handler for dispatched events.

        Args:
            exception (Exception): The exception from the dispatched event.
        """
        traceback.print_exception(type(exception), exception, exception.__traceback__)

    def override_error_handler(self, func: CoroFunc) -> None:
        """Overrides a new error handler for dispatched events.

        Args:
            func (CoroFunc): The new error handler.
        """
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback provided is not a coroutine.")

        orig_handler_sig = inspect.signature(self.error_handler)
        new_handler_sig = inspect.signature(func)

        if orig_handler_sig.parameters != new_handler_sig.parameters:
            raise TypeError(
                "Overloaded error handler does not have the same parameters as original error handler."
            )

        setattr(self, "error_handler", func)
        _log.debug("Registered new error handler")

    # dispatch

    def dispatch(self, name: str, *args: Any, **kwargs: Any) -> None:
        """Dispatches a event. This will trigger the all of the event's
        callbacks.

        Args:
            name (str): The name of the event to dispatch.
            *args (Any): Arguments to pass into the event.
            **kwargs (Any): Keyword arguments to pass into the event.
        """
        _log.debug("Dispatching event %s", name)
        event = self.events.get(name)

        if event is not None:
            event.dispatch(*args, **kwargs)
