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

import asyncio
import datetime
import logging
import platform
import random
import zlib
from typing import Any, Optional, Union, cast

import aiohttp
from discord_typings import GatewayEvent

from discatcore.dispatcher import Dispatcher
from discatcore.enums import GatewayOpcode
from discatcore.errors import GatewayReconnect
from discatcore.gateway.ratelimiter import Ratelimiter
from discatcore.http import HTTPClient
from discatcore.types import Snowflake
from discatcore.utils import dumps, loads

__all__ = ("GatewayClient",)

_log = logging.getLogger(__name__)


class HeartbeatHandler:
    """A class that helps keep the Gateway connection alive.

    Args:
        parent (.GatewayClient): The parent reference of this heartbeat handler.

    Attributes:
        parent (.GatewayClient): The parent reference of this heartbeat handler.
    """

    __slots__ = (
        "parent",
        "_task",
        "_first_heartbeat",
    )

    def __init__(self, parent: GatewayClient):
        self.parent = parent
        self._first_heartbeat = True

    async def loop(self):
        while not self.parent.is_closed:
            try:
                delta = self.parent.heartbeat_interval
                if self._first_heartbeat:
                    delta *= random.uniform(0.0, 1.0)
                    self._first_heartbeat = False

                await self.parent.heartbeat()
                await asyncio.sleep(delta)
            except asyncio.CancelledError:
                break

    def start(self):
        self._task = asyncio.create_task(self.loop())

    async def stop(self):
        self._task.cancel()
        await self._task


class GatewayClient:
    # TODO: docs rework
    """The Gateway client that manages connections to and from the Discord API.

    Args:
        http (HTTPClient): The http client. This is used to create the websocket connection and to retrieve the token.
        dispatcher (Dispatcher): The dispatcher. This is used to dispatch events recieved over the gateway.
        heartbeat_timeout (int): The amount of time (in seconds) to wait for a heartbeat ack to come in.
            Defaults to 30 seconds.
        intents (int): The intents to use.

    Attributes:
        inflator (zlib.decompressobj): The compression inflator.
            This is used for messages that are compressed, which is enabled by default.
        heartbeat_interval (float): The interval to heartbeat given by Discord. This is used with the heartbeat handler.
        session_id (str): The session id of this Gateway connection. This is also used when we resume connection.
        recent_gp (.GatewayPayload): The newest Gateway Payload.
        heartbeat_timeout (int): The amount of time (in seconds) to wait for a heartbeat ack to come in.
        ratelimiter (.Ratelimiter): The ratelimiter for the Gateway connection.
            This is used to limit the number of commands (except for heartbeats) so we don't get kicked off of the
            gateway connection with opcode 9.
        heartbeat_handler (Optional[.HeartbeatHandler]): The heartbeat handler for the Gateway connection.
            This is used to keep the connection alive via Discord's guidelines.
    """

    __slots__ = (
        "_ws",
        "_inflator",
        "_http",
        "_dispatcher",
        "intents",
        "heartbeat_interval",
        "sequence",
        "session_id",
        "recent_payload",
        "can_resume",
        "heartbeat_handler",
        "ratelimiter",
        "_last_heartbeat_ack",
        "heartbeat_timeout",
    )

    def __init__(
        self,
        http: HTTPClient,
        dispatcher: Dispatcher,
        *,
        heartbeat_timeout: float = 30.0,
        intents: int = 0,
    ):
        # Internal attribs
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._inflator = zlib.decompressobj()
        self._http: HTTPClient = http
        self._dispatcher: Dispatcher = dispatcher

        # Values for the Gateway
        self.intents: int = intents

        # Values from the Gateway
        self.heartbeat_interval: float = 0.0
        self.sequence: Optional[int] = None
        self.session_id: str = ""
        self.recent_payload: Optional[GatewayEvent] = None
        self.can_resume: bool = False

        # Handlers
        self.heartbeat_handler: HeartbeatHandler = HeartbeatHandler(self)
        self.ratelimiter: Ratelimiter = Ratelimiter(self)
        self.ratelimiter.start()

        # Misc
        self._last_heartbeat_ack: Optional[datetime.datetime] = None
        self.heartbeat_timeout: float = heartbeat_timeout

    # Internal functions

    def _decompress_msg(self, msg: bytes):
        ZLIB_SUFFIX = b"\x00\x00\xff\xff"

        out_str: str = ""

        # Message should be compressed
        if len(msg) < 4 or msg[-4:] != ZLIB_SUFFIX:
            return out_str

        buff = self._inflator.decompress(msg)
        out_str = buff.decode("utf-8")
        return out_str

    async def send(self, data: dict[str, Any]):
        """Sends a dict payload to the websocket connection.

        Args:
            data (dict[str, Any]): The data to send to the websocket connection.
        """
        if not self._ws:
            return

        await self.ratelimiter.acquire()
        await self._ws.send_json(data, dumps=dumps)
        _log.debug("Sent JSON payload %s to the Gateway.", data)

    async def receive(self) -> Optional[bool]:
        """Receives a message from the websocket connection and decompresses the message.

        Returns:
            A bool correspoding to whether we received a message or not.
        """
        if not self._ws:
            return

        msg: aiohttp.WSMessage
        try:
            msg = await self._ws.receive()
        except asyncio.TimeoutError:
            # try to re-establish the connection with the Gateway
            await self.close(code=1012)
            return False

        # aiohttp.WSMessage has 0 typing
        # great job aio-libs

        _log.debug("Received WS message from Gateway with type %s", msg.type.name)  # type: ignore

        if msg.type in (aiohttp.WSMsgType.BINARY, aiohttp.WSMsgType.TEXT):  # type: ignore
            received_msg = None
            if msg.type == aiohttp.WSMsgType.BINARY:  # type: ignore
                received_msg = self._decompress_msg(msg.data)  # type: ignore
            elif msg.type == aiohttp.WSMsgType.TEXT:  # type: ignore
                received_msg = msg.data  # type: ignore

            self.recent_payload = cast(GatewayEvent, loads(received_msg))  # type: ignore
            _log.debug("Received payload from the Gateway: %s", self.recent_payload)
            self.sequence = self.recent_payload.get("s")
            return True
        elif msg.type == aiohttp.WSMsgType.CLOSE:  # type: ignore
            await self.close(reconnect=False)
            return False

    # Connection management

    async def connect(self, url: Optional[str] = None) -> asyncio.Task[None]:
        """Starts a connection with the Gateway.

        Args:
            url (Optional[str]): The url to connect to the Gateway with. This should only be used if we are resuming.
                If this is not provided, then the url will be fetched via the Get Gateway Bot endpoint. Defaults to None.

        Returns:
            An `asyncio.Task` that is running the connection loop.
        """
        if not url:
            url = (await self._http.get_gateway_bot())["url"]

        self._ws = await self._http.ws_connect(url)

        res = await self.receive()
        if res and self.recent_payload is not None and self.recent_payload["op"] == 10:
            self.heartbeat_interval = self.recent_payload["d"].get("heartbeat_interval")
        else:
            # I guess Discord is having issues today if we get here
            # Disconnect and DO NOT ATTEMPT a reconnection
            await self.close(reconnect=False)

        self.heartbeat_handler.start()
        if self.can_resume:
            await self.resume()
        else:
            await self.identify()

        return asyncio.create_task(self.connection_loop())

    async def connection_loop(self):
        """Executes the main Gateway loop, which is the following:

        - compare the last time the heartbeat ack was sent from the server to current time
            - if that comparison is greater than the heartbeat timeout, then we reconnect
        - receive the latest message from the server via :meth:`.receive`
        - poll the latest message and perform an action based on that payload
        """
        if not self._ws:
            return

        while not self.is_closed:
            if (
                self._last_heartbeat_ack
                and (datetime.datetime.now() - self._last_heartbeat_ack).total_seconds()
                > self.heartbeat_timeout
            ):
                _log.debug("Zombified connection detected. Closing connection with code 1008.")
                await self.close(code=1008)
                break

            res = await self.receive()

            if res and self.recent_payload is not None:
                op = int(self.recent_payload["op"])
                if op == GatewayOpcode.DISPATCH and self.recent_payload.get("t") is not None:
                    event_name = str(self.recent_payload.get("t")).lower()
                    self._dispatcher.dispatch(event_name, self.recent_payload.get("d"))

                # these should be rare, but it's better to be safe than sorry
                elif op == GatewayOpcode.HEARTBEAT:
                    await self.heartbeat()

                elif op == GatewayOpcode.RECONNECT:
                    await self.close(code=1012)
                    break

                elif op == GatewayOpcode.INVALID_SESSION:
                    self.can_resume = bool(self.recent_payload.get("t"))
                    await self.close(code=1012)
                    break

                elif op == GatewayOpcode.HEARTBEAT_ACK:
                    self._last_heartbeat_ack = datetime.datetime.now()

    async def close(self, *, code: int = 1000, reconnect: bool = True, resume_url: str = ""):
        """Closes the connection with the websocket.

        Args:
            code (int): The websocket code to close with. Defaults to 1000.
            reconnect (bool): If we should reconnect or not. Defaults to True.
        """
        if not self._ws:
            return

        if not self._ws.closed:
            _log.info(
                "Closing Gateway connection with code %d that %s reconnect.",
                code,
                "will" if reconnect else "will not",
            )

            # Close the websocket connection
            await self._ws.close(code=code)

            # Clean up lingering tasks (this will throw exceptions if we get the client to do it)
            await self.ratelimiter.stop()
            if self.heartbeat_handler:
                await self.heartbeat_handler.stop()

            # if we need to reconnect, set the event
            if reconnect:
                raise GatewayReconnect(resume_url, self.can_resume)

    # Payloads

    @property
    def identify_payload(self):
        """:dict[str, Any]: Returns the identifcation payload."""
        identify_dict = {
            "op": GatewayOpcode.IDENTIFY.value,
            "d": {
                "token": self._http.token,
                "intents": self.intents,
                "properties": {
                    "os": platform.uname().system,
                    "browser": "discatcore",
                    "device": "discatcore",
                },
                "large_threshold": 250,
            },
        }

        # TODO: Presence support

        return identify_dict

    @property
    def resume_payload(self):
        """:dict[str, Any]: Returns the resume payload."""
        return {
            "op": GatewayOpcode.RESUME.value,
            "d": {
                "token": self._http.token,
                "session_id": self.session_id,
                "seq": self.sequence,
            },
        }

    @property
    def heartbeat_payload(self):
        """:dict[str, Any]: Returns the heartbeat payload."""
        return {"op": GatewayOpcode.HEARTBEAT.value, "d": self.sequence}

    # Gateway commands

    async def heartbeat(self):
        """Sends the heartbeat payload to the Gateway."""
        await self.send(self.heartbeat_payload)

    async def identify(self):
        """Sends the identify payload to the Gateway."""
        await self.send(self.identify_payload)

    async def resume(self):
        """Sends the resume payload to the Gateway."""
        await self.send(self.resume_payload)

    async def request_guild_members(
        self,
        guild_id: Snowflake,
        *,
        user_ids: Optional[Union[Snowflake, list[Snowflake]]] = None,
        limit: int = 0,
        query: str = "",
        presences: bool = False,
    ):
        """Sends the request guild members payload to the Gateway.

        Args:
            guild_id (int): The guild ID we are requesting members from.
            user_ids (Optional[Union[int, List[int]]]): The user id(s) to request. Defaults to None.
            limit (int): The maximum amount of members to grab. Defaults to 0.
            query (str): The string the username starts with. Defaults to "".
            presences (bool): Whether or not Discord should give us the presences of the members.
                Defaults to False.
        """
        payload: dict[str, Any] = {
            "op": GatewayOpcode.REQUEST_GUILD_MEMBERS.value,
            "d": {
                "guild_id": str(guild_id),
                "query": query,
                "limit": limit,
                "presences": presences,
            },
        }

        if user_ids is not None:
            payload["d"]["user_ids"] = user_ids

        await self.send(payload)

    async def update_presence(self, *, since: int, status: str, afk: bool):
        """Sends the update presence payload to the Gateway.

        Args:
            since (int): When the bot went AFK.
            status (str): The new status of the presence.
            afk (bool): Whether or not the bot is AFK or not.
        """
        payload: dict[str, Any] = {
            "op": GatewayOpcode.PRESENCE_UPDATE.value,
            "d": {
                "since": since,
                "activities": [],
                "status": status,
                "afk": afk,
            },
        }

        # TODO: Activities

        await self.send(payload)

    async def update_voice_state(
        self,
        *,
        guild_id: Snowflake,
        channel_id: Optional[Snowflake],
        self_mute: bool,
        self_deaf: bool,
    ):
        """Sends the update voice state payload to the Gateway.

        Args:
            guild_id (Snowflake): The id of the guild where the voice channel is in.
            channel_id (Optional[Snowflake]): The id of the voice channel. Set this to None if you want to disconnect.
            self_mute (bool): Whether the bot is muted or not.
            self_deaf (bool): Whether the bot is deafened or not.
        """
        await self.send(
            {
                "op": GatewayOpcode.VOICE_STATE_UPDATE.value,
                "d": {
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "self_mute": self_mute,
                    "self_deaf": self_deaf,
                },
            }
        )

    # Misc

    @property
    def is_closed(self):
        if not self._ws:
            return False

        return self._ws.closed
