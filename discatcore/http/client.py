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
from datetime import datetime
from types import EllipsisType
from typing import Any, Optional, cast
from urllib.parse import quote as _urlquote

import aiohttp
from discord_typings import GetGatewayBotData

from discatcore import __version__
from discatcore.errors import HTTPException, UnsupportedAPIVersionWarning
from discatcore.file import BasicFile
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


def _calculate_reset_after(resp: aiohttp.ClientResponse) -> float:
    headers = resp.headers

    if "X-RateLimit-Reset" in headers:
        now = datetime.now()
        reset = datetime.fromtimestamp(float(headers.get("X-RateLimit-Reset", 0.0)))
        reset_after = (reset - now).total_seconds()
    else:
        reset_after = float(headers.get("X-RateLimit-Reset-After", 0.0))

    return reset_after if reset_after >= 0.0 else 0.0


def _filter_dict_for_unset(d: dict[Any, Any]):
    return dict(filter(lambda item: item[1] is not Unset, d.items()))


class HTTPClient:
    __slots__ = (
        "token",
        "_ratelimiter",
        "_api_version",
        "_api_url",
        "__session",
        "user_agent",
        "default_headers",
        "request_id",
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
        self.request_id = 0

    @property
    def _session(self):
        if self.__session is None or self.__session.closed:  # type: ignore
            self.__session = aiohttp.ClientSession(
                headers={"User-Agent": self.user_agent}, json_serialize=dumps
            )

        return self.__session

    async def ws_connect(self, url: str):
        """Starts a websocket connection.

        Parameters
        ----------
        url: :class:`str`
            The url of the websocket to connect to.
        """
        kwargs = {
            "max_msg_size": 0,
            "timeout": 30.0,
            "autoclose": False,
            "headers": {"User-Agent": self.user_agent},
            "compress": 0,
        }

        return await self._session.ws_connect(url, **kwargs)

    async def close(self):
        """Closes the connection."""
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

            # this has to be done because otherwise Pyright will complain about files not being an iterable type
            if isinstance(files, list):
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
        self.request_id += 1
        rid = self.request_id
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

        bucket = self._ratelimiter.get_bucket(route)
        supports_ratelimits = False  # there are some special routes that have 0 ratelimiting

        for tries in range(max_tries):
            await self._ratelimiter.global_bucket.wait()
            await bucket.wait()
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

            supports_ratelimits = response.headers.get("X-RateLimit-Bucket") is not None

            reset_after = 0.0
            remaining = 0
            if supports_ratelimits:
                reset_after = _calculate_reset_after(response)
                remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
            else:
                _log.debug(
                    "REQUEST:%d Bucket %s does not have any ratelimiting.", rid, route.bucket
                )

            # Everything is ok
            if 200 <= response.status < 300:
                if supports_ratelimits:
                    if remaining == 0 and reset_after > 0.0:
                        _log.debug(
                            "REQUEST:%d Ratelimit bucket %s has expired. Waiting to refresh it.",
                            rid,
                            route.bucket,
                        )
                        bucket.lock_for(reset_after)
                        await bucket.wait()
                        _log.debug(
                            "REQUEST:%d Ratelimit bucket %s is good to go!", rid, route.bucket
                        )
                return await self._text_or_json(response)

            # Ratelimited
            if response.status == 429:
                if "Via" not in response.headers:
                    # something about Cloudflare and Google responding and adding something to the headers
                    # it means we're Cloudflare banned
                    raise HTTPException(response, await self._text_or_json(response))

                if supports_ratelimits:
                    retry_after = float(response.headers["Retry-After"])
                    is_global = response.headers["X-RateLimit-Scope"] == "global"

                    if is_global:
                        _log.info(
                            "REQUEST:%d All requests have hit a global ratelimit! Retrying in %f.",
                            rid,
                            retry_after,
                        )
                        self._ratelimiter.global_bucket.lock_for(retry_after)
                        await self._ratelimiter.global_bucket.wait()
                    else:
                        _log.info(
                            "REQUEST:%d Requests with bucket %s have hit a ratelimit! Retrying in %f.",
                            rid,
                            route.bucket,
                            reset_after,
                        )
                        bucket.lock_for(retry_after)
                        await bucket.wait()

                    _log.info("REQUEST:%d Ratelimit is over. Continuing with the request.", rid)
                else:
                    raise RuntimeError(
                        f"Route {route.bucket} that doesn't support ratelimiting hit a 429?"
                    )

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
        gb_info = await self.request(Route("GET", "/gateway/bot"))
        return cast(GetGatewayBotData, gb_info)

    async def get_from_cdn(self, url: str) -> bytes:
        async with self._session.get(url) as resp:
            if resp.status == 200:
                return await resp.read()

            raise HTTPException(resp, f"failed to get CDN Asset with url {url}")
