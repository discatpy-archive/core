# SPDX-License-Identifier: MIT

from typing import Any, Optional
from urllib.parse import quote as _urlquote

from ..types import Snowflake

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
        top_level_params = {
            k: getattr(self, k)
            for k in ("guild_id", "channel_id", "webhook_id", "webhook_token")
            if getattr(self, k) is not None
        }
        other_params = {k: None for k in self.params.keys() if k not in top_level_params.keys()}

        return f"{self.method}:{self.url.format_map({**top_level_params, **other_params})}"
