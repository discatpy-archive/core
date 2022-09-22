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
from typing import TYPE_CHECKING, Any, Optional, Union, cast

import aiohttp

from discatcore.enums import GatewayOpcode
from discatcore.gateway.ratelimiter import Ratelimiter
from discatcore.gateway.types import GatewayPayload
from discatcore.types import Snowflake
from discatcore.utils import dumps, loads

if TYPE_CHECKING:
    from discatcore.client import Client

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

        self._task = asyncio.create_task(self.loop())

    async def loop(self):
        while not self.parent.ws.closed:
            try:
                await self.parent.send(self.parent.heartbeat_payload)

                delta = self.parent.heartbeat_interval
                if self._first_heartbeat:
                    delta *= random.uniform(0.0, 1.0)
                    self._first_heartbeat = False

                await asyncio.sleep(delta)
            except asyncio.CancelledError:
                break

    async def stop(self):
        self._task.cancel()
        await self._task


class GatewayClient:
    """The Gateway client that manages connections to and from the Discord API.

    Args:
        ws (aiohttp.ClientWebSocketResponse): The websocket client. This is created via the :class:`HTTPClient` client.
        client (Client): The parent client. This is used for dispatching events recieved from the gateway.
        heartbeat_timeout (int): The amount of time (in seconds) to wait for a heartbeat ack to come in.
            Defaults to 30 seconds.

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
        "ws",
        "inflator",
        "client",
        "heartbeat_interval",
        "_sequence",
        "session_id",
        "recent_gp",
        "_last_heartbeat_ack",
        "heartbeat_timeout",
        "_gateway_resume",
        "ratelimiter",
        "heartbeat_handler",
    )

    def __init__(
        self,
        ws: aiohttp.ClientWebSocketResponse,
        client: Client,
        heartbeat_timeout: float = 30.0,
    ):
        self.ws: aiohttp.ClientWebSocketResponse = ws
        self.inflator = zlib.decompressobj()
        self.client: Client = client
        self.heartbeat_interval: float = 0.0
        self._sequence: Optional[int] = None
        self.session_id: str = ""
        self.recent_gp: Optional[GatewayPayload] = None
        self._last_heartbeat_ack: datetime.datetime = datetime.datetime.now()
        self.heartbeat_timeout: float = heartbeat_timeout
        self._gateway_resume: bool = False
        self.ratelimiter = Ratelimiter(self)
        self.ratelimiter.start()
        self.heartbeat_handler: Optional[HeartbeatHandler] = None

    def _decompress_msg(self, msg: bytes):
        ZLIB_SUFFIX = b"\x00\x00\xff\xff"

        out_str: str = ""

        # Message should be compressed
        if len(msg) < 4 or msg[-4:] != ZLIB_SUFFIX:
            return out_str

        buff = self.inflator.decompress(msg)
        out_str = buff.decode("utf-8")
        return out_str

    async def send(self, data: dict[str, Any]):
        """Sends a dict payload to the websocket connection.

        Args:
            data (dict[str, Any]): The data to send to the websocket connection.
        """
        await self.ratelimiter.acquire()
        await self.ws.send_json(data, dumps=dumps)
        _log.debug("Sent JSON payload %s to the Gateway.", data)

    async def receive(self):
        """Receives a message from the websocket connection and decompresses the message.

        Returns:
            A bool correspoding to whether we received a message or not.
        """
        msg: aiohttp.WSMessage
        try:
            msg = await self.ws.receive()
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

            self.recent_gp = cast(GatewayPayload, loads(received_msg))  # type: ignore
            _log.debug("Received payload from the Gateway: %s", self.recent_gp)
            self._sequence = self.recent_gp.get("s")
            return True
        elif msg.type == aiohttp.WSMsgType.CLOSE:  # type: ignore
            await self.close(reconnect=False)
            return False

    async def close(self, code: int = 1000, reconnect: bool = True):
        """Closes the connection with the websocket.

        Args:
            code (int): The websocket code to close with. Defaults to 1000.
            reconnect (bool): If we should reconnect or not. Defaults to True.
        """
        if not self.ws.closed:
            _log.info(
                "Closing Gateway connection with code %d that %s reconnect.",
                code,
                "will" if reconnect else "will not",
            )

            # Close the websocket connection
            await self.ws.close(code=code)

            # Clean up lingering tasks (this will throw exceptions if we get the client to do it)
            await self.ratelimiter.stop()
            if self.heartbeat_handler:
                await self.heartbeat_handler.stop()

            # if we need to reconnect, set the event
            if reconnect:
                # TODO: raise exception instead of accessing a private method
                self.client._gateway_reconnect.set()

    @property
    def identify_payload(self):
        """:dict[str, Any]: Returns the identifcation payload."""
        identify_dict = {
            "op": GatewayOpcode.IDENTIFY.value,
            "d": {
                "token": self.client.token,
                "intents": self.client.intents.value,
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
                "token": self.client.token,
                "session_id": self.session_id,
                "seq": self._sequence,
            },
        }

    @property
    def heartbeat_payload(self):
        """:dict[str, Any]: Returns the heartbeat payload."""
        return {"op": GatewayOpcode.HEARTBEAT.value, "d": self._sequence}

    async def loop(self):
        """Executes the main Gateway loop, which is the following:

        - compare the last time the heartbeat ack was sent from the server to current time
            - if that comparison is greater than the heartbeat timeout, then we reconnect
        - receive the latest message from the server via :meth:`.receive`
        - poll the latest message and perform an action based on that payload
        """
        while not self.ws.closed:
            if self._gateway_resume:
                await self.send(self.resume_payload)
                _log.info("Resumed connection with the Gateway.")
                self._gateway_resume = False

            if (
                datetime.datetime.now() - self._last_heartbeat_ack
            ).total_seconds() > self.heartbeat_timeout:
                _log.debug("Zombified connection detected. Closing connection with code 1008.")
                await self.close(code=1008)
                break

            res = await self.receive()

            if res and self.recent_gp is not None:
                op = self.recent_gp.get("op")
                if op == GatewayOpcode.DISPATCH and self.recent_gp["t"] is not None:
                    event_name = self.recent_gp["t"].lower()
                    args = getattr(self.client.event_handler, f"handle_{event_name}")(
                        self.recent_gp["d"]
                    )
                    self.client.dispatch(event_name, *args)

                elif op == GatewayOpcode.RECONNECT:
                    await self.close(code=1012)
                    break

                elif op == GatewayOpcode.INVALID_SESSION:
                    resumable: bool = (
                        self.recent_gp["d"] if isinstance(self.recent_gp["d"], bool) else False
                    )
                    self._gateway_resume = resumable
                    await self.close(code=1012)
                    break

                elif op == GatewayOpcode.HELLO:
                    self.heartbeat_interval = self.recent_gp["d"]["heartbeat_interval"] / 1000  # type: ignore
                    await self.send(self.identify_payload)
                    self.heartbeat_handler = HeartbeatHandler(self)
                    _log.debug("Heartbeat handler has started.")

                elif op == GatewayOpcode.HEARTBEAT_ACK:
                    self._last_heartbeat_ack = datetime.datetime.now()

    async def request_guild_members(
        self,
        guild_id: Snowflake,
        *,
        user_ids: Optional[Union[Snowflake, list[Snowflake]]] = None,
        limit: int = 0,
        query: str = "",
        presences: bool = False,
    ):
        """Sends a guild members request to the Gateway.

        Args:
            guild_id (int): The guild ID we are requesting members from.
            user_ids (Optional[Union[int, List[int]]]): The user id(s) to request. Defaults to None.
            limit (int): The maximum amount of members to grab. Defaults to 0.
            query (str): The string the username starts with. Defaults to "".
            presences (bool): Whether or not Discord should give us the presences of the members.
                Defaults to False.
        """
        guild_mems_req: dict[str, Any] = {
            "op": GatewayOpcode.REQUEST_GUILD_MEMBERS.value,
            "d": {
                "guild_id": str(guild_id),
                "query": query,
                "limit": limit,
                "presences": presences,
            },
        }

        if user_ids is not None:
            guild_mems_req["d"]["user_ids"] = user_ids

        await self.send(guild_mems_req)

    async def update_presence(self, *, since: int, status: str, afk: bool):
        """Sends a presence update to the Gateway.

        Args:
            since (int): When the bot went AFK.
            activities (List[Activity]): The new activities for the presence.
            status (str): The new status of the presence.
            afk (bool): Whether or not the bot is AFK or not.
        """
        new_presence_dict: dict[str, Any] = {
            "op": GatewayOpcode.PRESENCE_UPDATE.value,
            "d": {
                "since": since,
                "activities": [],
                "status": status,
                "afk": afk,
            },
        }

        # TODO: Activities

        await self.send(new_presence_dict)
