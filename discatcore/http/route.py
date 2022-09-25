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

from typing import Any, Optional
from urllib.parse import quote as _urlquote

from discatcore.types import Snowflake

__all__ = ("Route",)


class Route:
    """Represents a Discord API route. This implements helpful methods that the internals use.

    Args:
        method (str): The method of this REST API route.
        url (str): The raw, unformatted url of this REST API route.
        **params (Any): The parameters for the raw, unformatted url.

    Attributes:
        params (dict[str, Any]): The parameters for the raw, unformatted url.
        method (str): The method of this REST API route.
        url (str): The raw, unformatted url of this REST API route.
        guild_id (Optional[Snowflake]): If included, the guild id parameter.
            This is a top-level parameter, which influences the pseudo-bucket generated.
        channel_id (Optional[Snowflake]): If included, the channel id parameter.
            This is a top-level parameter, which influences the pseudo-bucket generated.
        webhook_id (Optional[Snowflake]): If included, the webhook id parameter.
            This is a top-level parameter, which influences the pseudo-bucket generated.
        webhook_token (Optional[str]): If included, the webhook token parameter.
            This is a top-level parameter, which influences the pseudo-bucket generated.
    """

    def __init__(self, method: str, url: str, **params: Any):
        self.params = params
        self.method = method
        self.url = url

        # top-level resource parameters
        self.guild_id: Optional[Snowflake] = params.get("guild_id")
        self.channel_id: Optional[Snowflake] = params.get("channel_id")
        self.webhook_id: Optional[Snowflake] = params.get("webhook_id")
        self.webhook_token: Optional[str] = params.get("webhook_token")

    @property
    def endpoint(self) -> str:
        """The formatted url for this route."""
        return self.url.format_map({k: _urlquote(str(v)) for k, v in self.params.items()})

    @property
    def bucket(self) -> str:
        """The pseudo-bucket that represents this route. This is generated via the method, raw url and top level parameters."""
        available_top_level_params = [
            k
            for k in ("guild_id", "channel_id", "webhook_id", "webhook_token")
            if getattr(self, k, ...) is not ...
        ]
        top_level_params = {k: getattr(self, k) for k in available_top_level_params}

        # we can't use format_map here because that expects EVERYTHING to be
        # formatted in the string
        url = self.url
        for param_name, param in top_level_params.items():
            url = url.replace(f"{{{param_name}}}", str(param))

        return f"{self.method}:{url}"
