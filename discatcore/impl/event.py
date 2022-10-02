# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union

if TYPE_CHECKING:
    from .dispatcher import Dispatcher

_log = logging.getLogger(__name__)

__all__ = ("Event",)

T = TypeVar("T")
Func = Callable[..., T]
CoroFunc = Func[Coroutine[Any, Any, Any]]


@dataclass
class _EventCallbackMetadata:
    one_shot: bool = False
    parent: bool = False


class Event:
    """Represents an event for a dispatcher.

    Args:
        name (str): The name of this event.
        parent (Dispatcher): The parent dispatcher of this event.

    Attributes:
        name (str): The name of this event.
        parent (Dispatcher): The parent dispatcher of this event.
        callbacks (list[Callable[..., Coroutine[Any, Any, Any]]]): The callbacks for this event.
        metadata (dict[Callable[..., Coroutine[Any, Any, Any]], _EventCallbackMetadata]): The metadata for the callbacks for this event.
        _proto (Optional[inspect.Signature]): The prototype of this event.
            This will define what signature all of the callbacks will have.
        _error_handler (Callable[..., Coroutine[Any, Any, Any]]): The error handler of this event.
            The error handler will be run whenever an event dispatched raises an error.
            Defaults to the error handler from the parent dispatcher.
    """

    def __init__(self, name: str, parent: Dispatcher):
        self.name = name
        self.parent = parent
        self.callbacks: list[CoroFunc] = []
        self.metadata: dict[CoroFunc, _EventCallbackMetadata] = {}
        self._proto: Optional[inspect.Signature] = None
        self._error_handler: CoroFunc = self.parent.error_handler

    # setters/decorators

    def set_proto(self, proto_func: Func[Any], *, parent: bool = False):
        """Sets the prototype for this event.

        Args:
            proto_func (Callable[..., Any]): The prototype for this event.
            parent (bool): Whether or not this callback contains a self parameter. Defaults to False.
        """
        is_static = isinstance(proto_func, staticmethod)
        if is_static:
            proto_func = proto_func.__func__

        if not self._proto:
            sig = inspect.signature(proto_func)
            if parent and not is_static:
                new_params = list(sig.parameters.values())
                new_params.pop(0)
                sig = sig.replace(parameters=new_params)
            self._proto = sig

            _log.debug("Registered new event prototype under event %s", self.name)
        else:
            raise ValueError(f"Event prototype for event {self.name} has already been set!")

    def proto(
        self, func: Optional[Func[Any]] = None, *, parent: bool = False
    ) -> Union["Event", Callable[[Func[Any]], "Event"]]:
        """A decorator to set the prototype of this event.

        Args:
            func (Optional[Callable[..., Any]]): The prototype to pass into this decorator. Defaults to None.
            parent (bool): Whether or not this callback contains a self parameter. Defaults to False.

        Returns:
            Either this event object or a wrapper function that acts as the actual decorator.
            This depends on if the ``func`` arg was passed in.
        """

        def wrapper(func: Func[Any]):
            self.set_proto(func, parent=parent)
            return self

        if func:
            return wrapper(func)
        return wrapper

    def set_error_handler(self, func: CoroFunc):
        """Overrides the error handler of this event.

        Args:
            func (Callable[..., Coroutine[Any, Any, Any]]): The new error handler for this event.
        """
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback provided is not a coroutine.")

        orig_handler_sig = inspect.signature(self._error_handler)
        new_handler_sig = inspect.signature(func)

        if len(orig_handler_sig.parameters) != len(new_handler_sig.parameters):
            raise TypeError(
                "Overloaded error handler does not have the same parameters as original error handler."
            )

        self._error_handler = func
        _log.debug("Registered new error handler under event %s", self.name)

    def error_handler(self) -> Callable[[Func[Any]], "Event"]:
        """A decorator to override the error handler of this event.

        Returns:
            A wrapper function that acts as the actual decorator.
        """

        def wrapper(func: CoroFunc):
            self.set_error_handler(func)
            return self

        return wrapper

    def add_callback(self, func: CoroFunc, *, one_shot: bool = False, parent: bool = False):
        """Adds a new callback to this event.

        Args:
            func (Callable[..., Coroutine[Any, Any, Any]]): The callback to add to this event.
            one_shot (bool): Whether or not the callback should be a one shot (which means the callback will be removed after running). Defaults to False.
            parent (bool): Whether or not this callback contains a self parameter. Defaults to False.
        """
        if not self._proto:
            self.set_proto(func, parent=parent)
            # this is to prevent static type checkers from inferring that self._proto is
            # still None after setting it indirectly via a different function
            # (it should never go here tho because exceptions stop the flow of this code
            # and it should be set if we don't reach any exceptions)
            if not self._proto:
                return

        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Callback provided is not a coroutine.")

        callback_sig = inspect.signature(func)
        if parent:
            new_params = list(callback_sig.parameters.values())
            new_params.pop(0)
            callback_sig = callback_sig.replace(parameters=new_params)

        if len(self._proto.parameters) != len(callback_sig.parameters):
            raise TypeError(
                "Event callback parameters do not match up with the event prototype parameters."
            )

        metadat = _EventCallbackMetadata(one_shot)
        self.metadata[func] = metadat
        self.callbacks.append(func)

        _log.debug("Registered new event callback under event %s", self.name)

    def remove_callback(self, index: int):
        """Removes a callback located at a certain index.

        Args:
            index (int): The index where the callback is located.
        """
        if len(self.callbacks) - 1 < index:
            raise ValueError(f"Event {self.name} has less callbacks than the index provided!")

        del self.callbacks[index]
        _log.debug("Removed event callback with index %d under event %s", index, self.name)

    def callback(
        self, func: Optional[CoroFunc] = None, *, one_shot: bool = False, parent: bool = False
    ) -> Union["Event", Callable[[Func[Any]], "Event"]]:
        """A decorator to add a callback to this event.

        Args:
            func (Optional[Callable[..., Coroutine[Any, Any, Any]]]): The function to pass into this decorator. Defaults to None.
            one_shot (bool): Whether or not the callback should be a one shot (which means the callback will be removed after running). Defaults to False.
            parent (bool): Whether or not this callback contains a self parameter. Defaults to False.

        Returns:
            Either this event object or a wrapper function that acts as the actual decorator.
            This depends on if the ``func`` arg was passed in.
        """

        def wrapper(func: CoroFunc):
            self.add_callback(func, one_shot=one_shot, parent=parent)
            return self

        if func:
            return wrapper(func)
        return wrapper

    # dispatch

    async def _run(self, coro: CoroFunc, *args: Any, **kwargs: Any):
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            try:
                await self._error_handler(e)
            except asyncio.CancelledError:
                pass

    def _schedule_task(
        self,
        coro: CoroFunc,
        index: Optional[int],
        *args: Any,
        **kwargs: Any,
    ):
        task_name = f"DisCatCore Event:{self.name}"
        if index:
            task_name += f" Index:{index}"
        task_name = task_name.rstrip()

        wrapped = self._run(coro, *args, **kwargs)
        return asyncio.create_task(wrapped, name=task_name)

    def dispatch(self, *args: Any, **kwargs: Any):
        """Runs all event callbacks with arguments.

        Args:
            *args (Any): Arguments to pass into the event callbacks.
            **kwargs (Any): Keyword arguments to pass into the event callbacks.
        """
        for i, callback in enumerate(self.callbacks):
            metadata = self.metadata.get(callback, _EventCallbackMetadata())
            _log.debug("Running event callback under event %s with index %s", self.name, i)

            self._schedule_task(callback, i, *args, **kwargs)

            if metadata.one_shot:
                _log.debug("Removing event callback under event %s with index %s", self.name, i)
                self.remove_callback(i)
