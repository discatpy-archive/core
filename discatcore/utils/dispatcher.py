# SPDX-License-Identifier: MIT

from __future__ import annotations

import asyncio
import inspect
import logging
import traceback
import typing as t
from collections import defaultdict

import attr
from typing_extensions import Self, TypeGuard

from .event import Event, EventT, ExceptionEvent
from .json import JSONObject

if t.TYPE_CHECKING:
    from ..gateway import GatewayClient

_log = logging.getLogger(__name__)

__all__ = (
    "Consumer",
    "consumer_for",
    "Dispatcher",
)

T = t.TypeVar("T")
DispatcherT = t.TypeVar("DispatcherT", bound="Dispatcher")
ListenerCallbackT = t.TypeVar("ListenerCallbackT", bound="ListenerCallback[Event]")
Coro = t.Coroutine[T, t.Any, t.Any]

ListenerCallback = t.Callable[[EventT], Coro[None]]
ConsumerCallback = t.Callable[[DispatcherT, "GatewayClient", JSONObject], Coro[None]]


@attr.define
class Consumer(t.Generic[DispatcherT]):
    """Represents a dispatcher consumer. A consumer consumes a raw event and performs actions based on the raw event."""

    callback: ConsumerCallback[DispatcherT]
    events: tuple[str, ...]


def consumer_for(
    *events: str,
) -> t.Callable[[ConsumerCallback[DispatcherT]], Consumer[DispatcherT]]:
    def wrapper(func: ConsumerCallback[DispatcherT]) -> Consumer[DispatcherT]:
        return Consumer(func, events)

    return wrapper


def _is_exception_event(e: EventT) -> TypeGuard[ExceptionEvent[EventT]]:
    return isinstance(e, ExceptionEvent)


class Dispatcher:
    """A class that helps manage events."""

    __slots__ = ("_listeners", "_consumers")

    def __init__(self) -> None:
        self._listeners: defaultdict[type[Event], list[ListenerCallback[Event]]] = defaultdict(
            list
        )
        self._consumers: dict[str, Consumer[Self]] = {}

        for name, value in inspect.getmembers(self):
            if not isinstance(value, Consumer):
                continue

            self._consumers[name.lower()] = value

            for event_name in value.events:
                self._consumers[event_name.lower()] = value

    async def _run_listener(self, event: EventT, listener: ListenerCallback[EventT]) -> None:
        try:
            await listener(event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if _is_exception_event(event):
                _log.error(
                    "There was an error while running the listener callback (%s%s) under exception event %s.%s: %s",
                    listener.__name__,
                    inspect.signature(listener),
                    type(event).__module__,
                    type(event).__qualname__,
                    traceback.format_exception(type(e), e, e.__traceback__),
                )
            else:
                exec_event = ExceptionEvent(
                    exception=e, failed_event=event, failed_listener=listener
                )

                _log.info(
                    "An exception occured while handling %s.%s.",
                    type(event).__module__,
                    type(event).__qualname__,
                )
                await self.dispatch(exec_event)

    async def _handle_consumer(
        self, consumer: ConsumerCallback[Self], gateway: GatewayClient, payload: JSONObject
    ):
        try:
            await consumer(self, gateway, payload)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            asyncio.get_running_loop().call_exception_handler(
                {
                    "message": "An exception occured while consuming a raw event.",
                    "exception": e,
                    "task": asyncio.current_task(),
                }
            )

    def subscribe(self, event: type[EventT], func: ListenerCallback[EventT]) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"listener callback {func.__name__!r} has to be a coroutine function!")

        _log.debug(
            "Subscribing listener callback (%s%s) to event %s.%s",
            func.__name__,
            inspect.signature(func),
            event.__module__,
            event.__qualname__,
        )
        self._listeners[event].append(func)  # pyright: ignore

    def unsubscribe(self, event: type[EventT], func: ListenerCallback[EventT]) -> None:
        listeners = self._listeners.get(event)
        if not listeners:
            return

        _log.debug(
            "Unsubscribing listener callback (%s%s) from event %s.%s",
            func.__name__,
            inspect.signature(func),
            event.__module__,
            event.__qualname__,
        )
        listeners.remove(func)  # pyright: ignore

        if not listeners:
            del self._listeners[event]

    def listen_to(
        self,
        *,
        events: list[type[EventT]]
    ) -> t.Callable[[ListenerCallback[EventT]], ListenerCallback[EventT]]:
        def wrapper(func: ListenerCallback[EventT]) -> ListenerCallback[EventT]:
            for event in events:
                self.subscribe(event, func)

            return func

        return wrapper

    def dispatch(self, event: Event) -> asyncio.Future[t.Any]:
        _log.debug(
            "Dispatching event %s.%s (which dispatches event(s) %r).",
            type(event).__module__,
            type(event).__qualname__,
            [f"{e.__module__}.{e.__qualname__}" for e in event.dispatches],
        )
        dispatched: t.List[Coro[None]] = []

        for event_type in event.dispatches:
            for listener in self._listeners.get(event_type, []):
                dispatched.append(self._run_listener(event, listener))

        def _completed_future() -> asyncio.Future[None]:
            future = asyncio.get_running_loop().create_future()
            future.set_result(None)
            return future

        return asyncio.gather(*dispatched) if dispatched else _completed_future()

    def consume(self, event: str, gateway: GatewayClient, payload: JSONObject):
        consumer = self._consumers.get(event)

        if not consumer:
            _log.info("Consumer %s does not exist. Skipping consumption.", event)
            return

        _log.debug("Consuming raw event %s.", event)
        asyncio.create_task(
            self._handle_consumer(consumer.callback, gateway, payload),
            name=f"DisCatCore Consumer {event}",
        )
