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

__all__ = ("AutoModerationEndpoints",)


class AutoModerationEndpoints(EndpointMixin):
    async def list_auto_moderation_rules(self, guild_id: Snowflake):
        return await self.request(
            Route("GET", "/guilds/{guild_id}/auto-moderation/rules", guild_id=guild_id)
        )

    async def get_auto_moderation_rule(
        self, guild_id: Snowflake, auto_moderation_rule_id: Snowflake
    ):
        return await self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/auto-moderation/rules/{auto_moderation_rule_id}",
                guild_id=guild_id,
                auto_moderation_rule_id=auto_moderation_rule_id,
            )
        )

    async def create_auto_moderation_rule(
        self,
        guild_id: Snowflake,
        *,
        name: str,
        event_type: int,
        trigger_type: int,
        trigger_metadata: dict[str, Any] = Unset,
        actions: list[discord_typings.AutoModerationActionData],
        enabled: bool = Unset,
        exempt_roles: list[Snowflake] = Unset,
        exempt_channels: list[Snowflake] = Unset,
        reason: Optional[str] = None,
    ):
        return await self.request(
            Route("POST", "/guilds/{guild_id}/auto-moderation/rules", guild_id=guild_id),
            json_params={
                "name": name,
                "event_type": event_type,
                "trigger_type": trigger_type,
                "trigger_metadata": trigger_metadata,
                "actions": actions,
                "enabled": enabled,
                "exempt_roles": exempt_roles,
                "exempt_channels": exempt_channels,
            },
            reason=reason,
        )

    async def modify_auto_moderation_rule(
        self,
        guild_id: Snowflake,
        auto_moderation_rule_id: Snowflake,
        *,
        name: str = Unset,
        event_type: int = Unset,
        trigger_type: int = Unset,
        trigger_metadata: dict[str, Any] = Unset,
        actions: list[discord_typings.AutoModerationActionData] = Unset,
        enabled: bool = Unset,
        exempt_roles: list[Snowflake] = Unset,
        exempt_channels: list[Snowflake] = Unset,
        reason: Optional[str] = None,
    ):
        return await self.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/auto-moderation/rules/{auto_moderation_rule_id}",
                guild_id=guild_id,
                auto_moderation_rule_id=auto_moderation_rule_id,
            ),
            json_params={
                "name": name,
                "event_type": event_type,
                "trigger_type": trigger_type,
                "trigger_metadata": trigger_metadata,
                "actions": actions,
                "enabled": enabled,
                "exempt_roles": exempt_roles,
                "exempt_channels": exempt_channels,
            },
            reason=reason,
        )

    async def delete_auto_moderation_rule(
        self, guild_id: Snowflake, auto_moderation_rule_id: Snowflake, reason: Optional[str] = None
    ):
        return await self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/auto-moderation/rules/{auto_moderation_rule_id}",
                guild_id=guild_id,
                auto_moderation_rule_id=auto_moderation_rule_id,
            ),
            reason=reason,
        )