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

# this file was auto-generated by scripts/generate_endpoints.py

from typing import Any, Optional, Union

import discord_typings
from discord_typings import Snowflake

from discatcore.file import BasicFile
from discatcore.http.endpoints.core import EndpointMixin
from discatcore.http.route import Route
from discatcore.types import Unset

__all__ = ("InviteEndpoints",)


class InviteEndpoints(EndpointMixin):
    def get_invite(
        self,
        invite_code: Snowflake,
        *,
        with_counts: bool = Unset,
        with_expiration: bool = Unset,
        guild_scheduled_event_id: Snowflake = Unset,
    ):
        return self.request(
            Route("GET", "/invites/{invite_code}", invite_code=invite_code),
            query_params={
                "with_counts": with_counts,
                "with_expiration": with_expiration,
                "guild_scheduled_event_id": guild_scheduled_event_id,
            },
        )

    def delete_invite(self, invite_code: Snowflake, reason: Optional[str] = None):
        return self.request(
            Route("DELETE", "/invites/{invite_code}", invite_code=invite_code), reason=reason
        )
