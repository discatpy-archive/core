# SPDX-License-Identifier: MIT

# this file was auto-generated by scripts/generate_endpoints.py

from typing import Optional

import discord_typings
from discord_typings import Snowflake

from ...types import Unset
from ..route import Route
from .core import EndpointMixin

__all__ = ("GuildScheduledEventEndpoints",)


class GuildScheduledEventEndpoints(EndpointMixin):
    def list_scheduled_events_for_guild(
        self, guild_id: Snowflake, *, with_user_count: bool = Unset
    ):
        return self.request(
            Route("GET", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id),
            query_params={"with_user_count": with_user_count},
        )

    def create_guild_scheduled_event(
        self,
        guild_id: Snowflake,
        *,
        channel_id: Snowflake = Unset,
        entity_metadata: discord_typings.GuildScheduledEventEntityMetadata = Unset,
        name: str,
        privacy_level: int,
        scheduled_start_time: str,
        scheduled_end_time: str = Unset,
        description: str = Unset,
        entity_type: int,
        image: str = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("POST", "/guilds/{guild_id}/scheduled-events", guild_id=guild_id),
            json_params={
                "channel_id": channel_id,
                "entity_metadata": entity_metadata,
                "name": name,
                "privacy_level": privacy_level,
                "scheduled_start_time": scheduled_start_time,
                "scheduled_end_time": scheduled_end_time,
                "description": description,
                "entity_type": entity_type,
                "image": image,
            },
            reason=reason,
        )

    def get_guild_scheduled_event(
        self,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        *,
        with_user_count: bool = Unset,
    ):
        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}",
                guild_id=guild_id,
                guild_scheduled_event_id=guild_scheduled_event_id,
            ),
            query_params={"with_user_count": with_user_count},
        )

    def modify_guild_scheduled_event(
        self,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        *,
        channel_id: Snowflake = Unset,
        entity_metadata: Optional[discord_typings.GuildScheduledEventEntityMetadata] = Unset,
        name: str = Unset,
        privacy_level: int = Unset,
        scheduled_start_time: str = Unset,
        scheduled_end_time: str = Unset,
        description: Optional[str] = Unset,
        entity_type: int = Unset,
        image: str = Unset,
        status: int = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}",
                guild_id=guild_id,
                guild_scheduled_event_id=guild_scheduled_event_id,
            ),
            json_params={
                "channel_id": channel_id,
                "entity_metadata": entity_metadata,
                "name": name,
                "privacy_level": privacy_level,
                "scheduled_start_time": scheduled_start_time,
                "scheduled_end_time": scheduled_end_time,
                "description": description,
                "entity_type": entity_type,
                "image": image,
                "status": status,
            },
            reason=reason,
        )

    def delete_guild_scheduled_event(
        self, guild_id: Snowflake, guild_scheduled_event_id: Snowflake
    ):
        return self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}",
                guild_id=guild_id,
                guild_scheduled_event_id=guild_scheduled_event_id,
            )
        )

    def get_guild_scheduled_event_users(
        self,
        guild_id: Snowflake,
        guild_scheduled_event_id: Snowflake,
        *,
        limit: int = 100,
        with_member: bool = False,
        before: Snowflake = Unset,
        after: Snowflake = Unset,
    ):
        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/scheduled-events/{guild_scheduled_event_id}/users",
                guild_id=guild_id,
                guild_scheduled_event_id=guild_scheduled_event_id,
            ),
            query_params={
                "limit": limit,
                "with_member": with_member,
                "before": before,
                "after": after,
            },
        )
