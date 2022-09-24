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

import asyncio
import logging
import sys
import warnings
from dataclasses import dataclass
from typing import Any, Optional, cast
from urllib.parse import quote as _urlquote

import aiohttp
from discord_typings import GetGatewayBotData

from discatcore import __version__
from discatcore.errors import BucketMigrated, HTTPException, UnsupportedAPIVersionWarning
from discatcore.file import BasicFile
from discatcore.http.endpoints import *
from discatcore.http.ratelimiter import Ratelimiter
from discatcore.http.route import Route
from discatcore.types import Unset
from discatcore.utils import dumps, loads

BASE_API_URL = "https://discord.com/api/v{0}"
VALID_API_VERSIONS = [9, 10]
DEFAULT_API_VERSION = 10

__all__ = ("HTTPClient",)

_log = logging.getLogger(__name__)


@dataclass
class _PreparedData:
    json: Any = Unset
    multipart_content: aiohttp.FormData = Unset


def _filter_dict_for_unset(d: dict[Any, Any]):
    return dict(filter(lambda item: item[1] is not Unset, d.items()))


class HTTPClient(
    AuditLogEndpoints,
    AutoModerationEndpoints,
    ChannelEndpoints,
    EmojiEndpoints,
    GuildScheduledEventEndpoints,
    GuildTemplateEndpoints,
    GuildEndpoints,
    InviteEndpoints,
    StageInstanceEndpoints,
    StickerEndpoints,
    UserEndpoints,
    VoiceEndpoints,
):
    """The HTTP client that helps makes connections to the REST API. This handles ratelimiting and wraps
    Discord REST API endpoints into easy to use coroutine functions.

    Args:
        token (str): The bot token to use when sending a request to the Discord API.
            Normal user tokens WILL NOT WORK intentionally.
        api_version (Optional[int]): The Discord API version to use.
            It's not recommended to set this argument because this library will only
            be able to handle one API version at a time. Defaults to None.

    Attributes:
        token (str): The bot token to use when sending a request to the Discord API.
        user_agent (str): The user agent headers to use when sending a request to the Discord API.
            This contains the repo of this library, version of this library, and Python version.
        default_headers (dict[str, str]): Default headers to include in every request to the Discord API.
            This currently only includes the authorization headers, but the user agent header might be added too.
    """

    __slots__ = (
        "token",
        "_ratelimiter",
        "_api_version",
        "_api_url",
        "__session",
        "user_agent",
        "default_headers",
        "_request_id",
    )

    def __init__(self, token: str, *, api_version: Optional[int] = None):
        self.token = token
        self._ratelimiter = Ratelimiter()
        self._api_version = DEFAULT_API_VERSION

        if api_version is not None and api_version not in VALID_API_VERSIONS:
            warnings.warn(
                f"Discord API v{api_version} is not supported. v{DEFAULT_API_VERSION} will be used instead.",
                UnsupportedAPIVersionWarning,
            )
        elif api_version is not None:
            self._api_version = api_version

        self._api_url = BASE_API_URL.format(self._api_version)

        self.__session: Optional[aiohttp.ClientSession] = None
        self.user_agent = "DiscordBot (https://github.com/discatpy-dev/core, {0}) Python/{1.major}.{1.minor}.{1.micro}".format(
            __version__, sys.version_info
        )
        self.default_headers = {"Authorization": f"Bot {self.token}"}
        self._request_id = 0

    @property
    def _session(self):
        if self.__session is None or self.__session.closed:
            self.__session = aiohttp.ClientSession(
                headers={"User-Agent": self.user_agent}, json_serialize=dumps
            )

        return self.__session

    @property
    def api_version(self):
        """:int: The Discord API version to use."""
        return self._api_version

    async def ws_connect(self, url: str):
        """Starts a websocket connection.

        Args:
            url (str): The url of the websocket to connect to.
        """
        kwargs = {
            "max_msg_size": 0,
            "timeout": 30.0,
            "autoclose": False,
            "headers": {"User-Agent": self.user_agent},
            "compress": 0,
        }

        # this function is partially unknown
        # not our fault, aiohttp's fault
        return await self._session.ws_connect(url, **kwargs)  # type: ignore

    async def close(self):
        """Closes the HTTP session.
        If the HTTP session is attempted to be reused again then it'll be automatically regenerated.
        """
        if self.__session and not self.__session.closed:
            await self._session.close()

    @staticmethod
    def _prepare_data(json: dict[str, Any], files: list[BasicFile]):
        pd = _PreparedData()

        if json is not Unset and files is Unset:
            pd.json = _filter_dict_for_unset(json)

        if json is not Unset and files is not Unset:
            form_dat = aiohttp.FormData()
            form_dat.add_field(
                "payload_json", _filter_dict_for_unset(json), content_type="application/json"
            )

            for i, f in enumerate(files):
                form_dat.add_field(
                    f"files[{i}]", f.fp, content_type=f.content_type, filename=f.filename
                )

            pd.multipart_content = form_dat

        return pd

    @staticmethod
    async def _text_or_json(resp: aiohttp.ClientResponse):
        text = await resp.text()

        if resp.content_type == "application/json":
            return loads(text)

        return text

    async def request(
        self,
        route: Route,
        *,
        query_params: Optional[dict[str, Any]] = None,
        json_params: dict[str, Any] = Unset,
        reason: Optional[str] = None,
        files: list[BasicFile] = Unset,
        **extras: Any,
    ):
        """Sends a request to the Discord API. This automatically handles ratelimiting and data processing.

        Args:
            route (.Route): The route to send a request to.
            query_params (Optional[dict[str, Any]]): The query parameters to include in the url of this request.
                Any Unset values detected will be filtered out automatically. Defaults to None.
            json_params (dict[str, Any]): The json parameters to include in the request.
                Any Unset values detected will be filtered out automatically. Defaults to Unset.
            reason (Optional[str]): If this route supports reasons, the reason for the action caused by the
                route being performed. This will be included in the headers under "X-Audit-Log-Reason".
                Defaults to None.
            files (list[BasicFile]): The files to include in the request.
                This will be processed along with the json paramters to generate multipart content.
                Attachments are not automatically calculated in the json parameters.
                Defaults to Unset.
            **extras (Any): Any extra parameters to include in the underlying aiohttp request function.
                This SHOULD NOT be used by users, this is a internal parameter for special routes
                (like Create Guild Sticker).

        Returns:
            If this route returns any content, it will be processed and returned.
        """
        self._request_id += 1
        rid = self._request_id
        _log.debug("Request with id %d has started.", rid)
        url = route.endpoint

        query_params = _filter_dict_for_unset(query_params or {})
        max_tries = 5
        headers: dict[str, str] = self.default_headers

        if reason:
            headers["X-Audit-Log-Reason"] = _urlquote(reason, safe="/ ")

        data = self._prepare_data(json_params, files)
        kwargs: dict[str, Any] = extras or {}

        if data.json is not Unset:
            kwargs["json"] = data.json

        if data.multipart_content is not Unset:
            kwargs["data"] = data.multipart_content

        bucket = self._ratelimiter.get_bucket(route.bucket)

        for tries in range(max_tries):
            async with self._ratelimiter.global_bucket:
                async with bucket:
                    _log.debug("REQUEST:%d All ratelimit buckets have been acquired!", rid)

                    response = await self._session.request(
                        route.method,
                        f"{self._api_url}{url}",
                        params=query_params,
                        headers=headers,
                        **kwargs,
                    )
                    _log.debug(
                        "REQUEST:%d Made request to %s with method %s.",
                        rid,
                        f"{self._api_url}{url}",
                        route.method,
                    )

                    URL_BUCKET = bucket.bucket is None
                    bucket.update_info(response)
                    await bucket.acquire()

                    if URL_BUCKET and bucket.bucket is not None:
                        try:
                            self._ratelimiter.migrate_bucket(route.bucket, bucket.bucket)
                        except BucketMigrated:
                            bucket = self._ratelimiter.get_bucket(route.bucket)

                    # Everything is ok
                    if 200 <= response.status < 300:
                        return await self._text_or_json(response)

                    # Ratelimited
                    if response.status == 429:
                        if "Via" not in response.headers:
                            # something about Cloudflare and Google responding and adding something to the headers
                            # it means we're Cloudflare banned
                            raise HTTPException(response, await self._text_or_json(response))

                        retry_after = float(response.headers["Retry-After"])
                        is_global = response.headers["X-RateLimit-Scope"] == "global"

                        if is_global:
                            _log.info(
                                "REQUEST:%d All requests have hit a global ratelimit! Retrying in %f.",
                                rid,
                                retry_after,
                            )
                            self._ratelimiter.global_bucket.lock_for(retry_after)
                            await self._ratelimiter.global_bucket.acquire()

                        _log.info("REQUEST:%d Ratelimit is over. Continuing with the request.", rid)
                        continue

                    # Specific Server Errors, retry after some time
                    if response.status in {500, 502, 504}:
                        wait_time = 1 + tries * 2
                        _log.info("REQUEST:%d Got a server error! Retrying in %d.", rid, wait_time)
                        await asyncio.sleep(wait_time)
                        continue

                    # Client/Server errors
                    if response.status >= 400:
                        raise HTTPException(response, await self._text_or_json(response))

        raise RuntimeError(
            f'REQUEST:{rid} Tried sending request to "{url}" with method {route.method} {max_tries} times.'
        )

    async def get_gateway_bot(self) -> GetGatewayBotData:
        """Fetches the gateway information from the Discord API.

        Returns:
            A dict containing bot-specific gateway information (like shard_count, max_concurrency, etc).
        """
        gb_info = await self.request(Route("GET", "/gateway/bot"))
        return cast(GetGatewayBotData, gb_info)

    async def get_from_cdn(self, url: str) -> bytes:
        """Fetches an asset from the Discord CDN.
        Unlike the normal request function, these routes have 0 ratelimiting or data processing.

        Args:
            url (str): The url of the CDN asset to fetch.

        Returns:
            The raw bytes of the response (which is expected to be an image).
        """
        async with self._session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()

            raise HTTPException(resp, f"failed to get CDN Asset with url {url}")
