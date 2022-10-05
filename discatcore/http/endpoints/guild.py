# SPDX-License-Identifier: MIT

# this file was auto-generated by scripts/generate_endpoints.py

from typing import Optional

import discord_typings
from discord_typings import Snowflake

from ...types import Unset, UnsetOr
from ..route import Route
from .core import EndpointMixin

__all__ = ("GuildEndpoints",)


class GuildEndpoints(EndpointMixin):
    def create_guild(
        self,
        *,
        name: str,
        icon: UnsetOr[str] = Unset,
        verification_level: UnsetOr[discord_typings.VerificationLevels] = Unset,
        default_message_notifications: UnsetOr[
            discord_typings.DefaultMessageNotificationLevels
        ] = Unset,
        explicit_content_filter: UnsetOr[discord_typings.ExplicitContentFilterLevels] = Unset,
        roles: UnsetOr[list[discord_typings.RoleData]] = Unset,
        channels: UnsetOr[list[discord_typings.PartialChannelData]] = Unset,
        afk_channel_id: UnsetOr[Snowflake] = Unset,
        afk_timeout: UnsetOr[int] = Unset,
        system_channel_id: UnsetOr[Snowflake] = Unset,
        system_channel_flags: UnsetOr[int] = Unset,
    ):
        return self.request(
            Route("POST", "/guilds"),
            json_params={
                "name": name,
                "icon": icon,
                "verification_level": verification_level,
                "default_message_notifications": default_message_notifications,
                "explicit_content_filter": explicit_content_filter,
                "roles": roles,
                "channels": channels,
                "afk_channel_id": afk_channel_id,
                "afk_timeout": afk_timeout,
                "system_channel_id": system_channel_id,
                "system_channel_flags": system_channel_flags,
            },
        )

    def get_guild(self, guild_id: Snowflake, *, with_counts: bool = False):
        return self.request(
            Route("GET", "/guilds/{guild_id}", guild_id=guild_id),
            query_params={"with_counts": with_counts},
        )

    def get_guild_preview(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/preview", guild_id=guild_id))

    def modify_guild(
        self,
        guild_id: Snowflake,
        *,
        name: UnsetOr[str] = Unset,
        icon: UnsetOr[Optional[str]] = Unset,
        verification_level: UnsetOr[Optional[discord_typings.VerificationLevels]] = Unset,
        default_message_notifications: UnsetOr[
            Optional[discord_typings.DefaultMessageNotificationLevels]
        ] = Unset,
        explicit_content_filter: UnsetOr[
            Optional[discord_typings.ExplicitContentFilterLevels]
        ] = Unset,
        afk_channel_id: UnsetOr[Optional[Snowflake]] = Unset,
        afk_timeout: UnsetOr[int] = Unset,
        system_channel_id: UnsetOr[Optional[Snowflake]] = Unset,
        system_channel_flags: UnsetOr[int] = Unset,
        owner_id: UnsetOr[Snowflake] = Unset,
        splash: UnsetOr[Optional[str]] = Unset,
        discovery_splash: UnsetOr[Optional[str]] = Unset,
        banner: UnsetOr[Optional[str]] = Unset,
        rules_channel_id: UnsetOr[Optional[Snowflake]] = Unset,
        public_updates_channel_id: UnsetOr[Optional[Snowflake]] = Unset,
        preferred_locale: UnsetOr[Optional[str]] = Unset,
        features: UnsetOr[list[str]] = Unset,
        description: UnsetOr[Optional[str]] = Unset,
        premium_progress_bar_enabled: UnsetOr[bool] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("PATCH", "/guilds/{guild_id}", guild_id=guild_id),
            json_params={
                "name": name,
                "icon": icon,
                "verification_level": verification_level,
                "default_message_notifications": default_message_notifications,
                "explicit_content_filter": explicit_content_filter,
                "afk_channel_id": afk_channel_id,
                "afk_timeout": afk_timeout,
                "system_channel_id": system_channel_id,
                "system_channel_flags": system_channel_flags,
                "owner_id": owner_id,
                "splash": splash,
                "discovery_splash": discovery_splash,
                "banner": banner,
                "rules_channel_id": rules_channel_id,
                "public_updates_channel_id": public_updates_channel_id,
                "preferred_locale": preferred_locale,
                "features": features,
                "description": description,
                "premium_progress_bar_enabled": premium_progress_bar_enabled,
            },
            reason=reason,
        )

    def delete_guild(self, guild_id: Snowflake):
        return self.request(Route("DELETE", "/guilds/{guild_id}", guild_id=guild_id))

    def get_guild_channels(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/channels", guild_id=guild_id))

    def create_guild_channel(
        self,
        guild_id: Snowflake,
        *,
        name: str,
        type: UnsetOr[Optional[discord_typings.ChannelTypes]] = Unset,
        topic: UnsetOr[Optional[str]] = Unset,
        bitrate: UnsetOr[Optional[int]] = Unset,
        user_limit: UnsetOr[Optional[int]] = Unset,
        rate_limit_per_user: UnsetOr[Optional[int]] = Unset,
        position: UnsetOr[Optional[int]] = Unset,
        permission_overwrites: UnsetOr[
            Optional[list[discord_typings.PermissionOverwriteData]]
        ] = Unset,
        parent_id: UnsetOr[Optional[Snowflake]] = Unset,
        nsfw: UnsetOr[Optional[bool]] = Unset,
        rtc_region: UnsetOr[Optional[str]] = Unset,
        video_quality_mode: UnsetOr[Optional[discord_typings.VideoQualityModes]] = Unset,
        default_auto_archive_duration: UnsetOr[Optional[int]] = Unset,
        default_reaction_emoji: UnsetOr[Optional[discord_typings.DefaultReactionData]] = Unset,
        available_tags: UnsetOr[Optional[list[discord_typings.ForumTagData]]] = Unset,
        default_sort_order: UnsetOr[Optional[int]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("POST", "/guilds/{guild_id}/channels", guild_id=guild_id),
            json_params={
                "name": name,
                "type": type,
                "topic": topic,
                "bitrate": bitrate,
                "user_limit": user_limit,
                "rate_limit_per_user": rate_limit_per_user,
                "position": position,
                "permission_overwrites": permission_overwrites,
                "parent_id": parent_id,
                "nsfw": nsfw,
                "rtc_region": rtc_region,
                "video_quality_mode": video_quality_mode,
                "default_auto_archive_duration": default_auto_archive_duration,
                "default_reaction_emoji": default_reaction_emoji,
                "available_tags": available_tags,
                "default_sort_order": default_sort_order,
            },
            reason=reason,
        )

    def modify_guild_channel_positions(
        self,
        guild_id: Snowflake,
        *,
        id: Snowflake,
        position: UnsetOr[Optional[int]] = Unset,
        lock_permissions: UnsetOr[Optional[bool]] = Unset,
        parent_id: UnsetOr[Optional[Snowflake]] = Unset,
    ):
        return self.request(
            Route("PATCH", "/guilds/{guild_id}/channels", guild_id=guild_id),
            json_params={
                "id": id,
                "position": position,
                "lock_permissions": lock_permissions,
                "parent_id": parent_id,
            },
        )

    def list_active_guild_threads(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/threads/active", guild_id=guild_id))

    def get_guild_member(self, guild_id: Snowflake, user_id: Snowflake):
        return self.request(
            Route("GET", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id)
        )

    def list_guild_members(
        self, guild_id: Snowflake, *, limit: int = 1, after: UnsetOr[Snowflake] = Unset
    ):
        return self.request(
            Route("GET", "/guilds/{guild_id}/members", guild_id=guild_id),
            query_params={"limit": limit, "after": after},
        )

    def search_guild_members(self, guild_id: Snowflake, *, query: str, limit: int = 1):
        return self.request(
            Route("GET", "/guilds/{guild_id}/members/search", guild_id=guild_id),
            query_params={"query": query, "limit": limit},
        )

    def add_guild_member(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        access_token: str,
        nick: UnsetOr[str] = Unset,
        roles: UnsetOr[list[Snowflake]] = Unset,
        mute: UnsetOr[bool] = Unset,
        deaf: UnsetOr[bool] = Unset,
    ):
        return self.request(
            Route(
                "PUT", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id
            ),
            json_params={
                "access_token": access_token,
                "nick": nick,
                "roles": roles,
                "mute": mute,
                "deaf": deaf,
            },
        )

    def modify_guild_member(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        nick: UnsetOr[Optional[str]] = Unset,
        roles: UnsetOr[Optional[list[Snowflake]]] = Unset,
        mute: UnsetOr[Optional[bool]] = Unset,
        deaf: UnsetOr[Optional[bool]] = Unset,
        channel_id: UnsetOr[Optional[Snowflake]] = Unset,
        communication_disabled_until: UnsetOr[Optional[str]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route(
                "PATCH", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id
            ),
            json_params={
                "nick": nick,
                "roles": roles,
                "mute": mute,
                "deaf": deaf,
                "channel_id": channel_id,
                "communication_disabled_until": communication_disabled_until,
            },
            reason=reason,
        )

    def modify_current_member(
        self,
        guild_id: Snowflake,
        *,
        nick: UnsetOr[Optional[str]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("PATCH", "/guilds/{guild_id}/members/@me", guild_id=guild_id),
            json_params={"nick": nick},
            reason=reason,
        )

    def add_guild_member_role(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        role_id: Snowflake,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route(
                "PUT",
                "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            reason=reason,
        )

    def remove_guild_member_role(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        role_id: Snowflake,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            reason=reason,
        )

    def remove_guild_member(
        self, guild_id: Snowflake, user_id: Snowflake, reason: Optional[str] = None
    ):
        return self.request(
            Route(
                "DELETE", "/guilds/{guild_id}/members/{user_id}", guild_id=guild_id, user_id=user_id
            ),
            reason=reason,
        )

    def get_guild_bans(
        self,
        guild_id: Snowflake,
        *,
        limit: int = 1000,
        before: UnsetOr[Snowflake] = Unset,
        after: UnsetOr[Snowflake] = Unset,
    ):
        return self.request(
            Route("GET", "/guilds/{guild_id}/bans", guild_id=guild_id),
            query_params={"limit": limit, "before": before, "after": after},
        )

    def get_guild_ban(self, guild_id: Snowflake, user_id: Snowflake):
        return self.request(
            Route("GET", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id)
        )

    def create_guild_ban(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        delete_message_seconds: UnsetOr[int] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("PUT", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id),
            json_params={"delete_message_seconds": delete_message_seconds},
            reason=reason,
        )

    def remove_guild_ban(
        self, guild_id: Snowflake, user_id: Snowflake, reason: Optional[str] = None
    ):
        return self.request(
            Route(
                "DELETE", "/guilds/{guild_id}/bans/{user_id}", guild_id=guild_id, user_id=user_id
            ),
            reason=reason,
        )

    def get_guild_roles(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id))

    def create_guild_role(
        self,
        guild_id: Snowflake,
        *,
        name: UnsetOr[str] = Unset,
        permissions: UnsetOr[str] = Unset,
        color: UnsetOr[int] = Unset,
        hoist: UnsetOr[bool] = Unset,
        icon: UnsetOr[Optional[str]] = Unset,
        unicode_emoji: UnsetOr[Optional[str]] = Unset,
        mentionable: UnsetOr[bool] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("POST", "/guilds/{guild_id}/roles", guild_id=guild_id),
            json_params={
                "name": name,
                "permissions": permissions,
                "color": color,
                "hoist": hoist,
                "icon": icon,
                "unicode_emoji": unicode_emoji,
                "mentionable": mentionable,
            },
            reason=reason,
        )

    def modify_guild_role_positions(
        self,
        guild_id: Snowflake,
        *,
        id: Snowflake,
        position: UnsetOr[Optional[int]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("PATCH", "/guilds/{guild_id}/roles", guild_id=guild_id),
            json_params={"id": id, "position": position},
            reason=reason,
        )

    def modify_guild_role(
        self,
        guild_id: Snowflake,
        role_id: Snowflake,
        *,
        name: UnsetOr[Optional[str]] = Unset,
        permissions: UnsetOr[Optional[str]] = Unset,
        color: UnsetOr[Optional[int]] = Unset,
        hoist: UnsetOr[Optional[bool]] = Unset,
        icon: UnsetOr[Optional[str]] = Unset,
        unicode_emoji: UnsetOr[Optional[str]] = Unset,
        mentionable: UnsetOr[Optional[bool]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route(
                "PATCH", "/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id
            ),
            json_params={
                "name": name,
                "permissions": permissions,
                "color": color,
                "hoist": hoist,
                "icon": icon,
                "unicode_emoji": unicode_emoji,
                "mentionable": mentionable,
            },
            reason=reason,
        )

    def modify_guild_mfa_level(
        self, guild_id: Snowflake, *, level: discord_typings.MFALevels, reason: Optional[str] = None
    ):
        return self.request(
            Route("POST", "/guilds/{guild_id}/mfa", guild_id=guild_id),
            json_params={"level": level},
            reason=reason,
        )

    def delete_guild_role(
        self, guild_id: Snowflake, role_id: Snowflake, reason: Optional[str] = None
    ):
        return self.request(
            Route(
                "DELETE", "/guilds/{guild_id}/roles/{role_id}", guild_id=guild_id, role_id=role_id
            ),
            reason=reason,
        )

    def get_guild_prune_count(
        self, guild_id: Snowflake, *, days: int = 7, include_roles: UnsetOr[str] = Unset
    ):
        return self.request(
            Route("GET", "/guilds/{guild_id}/prune", guild_id=guild_id),
            query_params={"days": days, "include_roles": include_roles},
        )

    def begin_guild_prune(
        self,
        guild_id: Snowflake,
        *,
        days: int = 7,
        compute_prune_count: bool = True,
        include_roles: UnsetOr[list[Snowflake]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("POST", "/guilds/{guild_id}/prune", guild_id=guild_id),
            json_params={
                "days": days,
                "compute_prune_count": compute_prune_count,
                "include_roles": include_roles,
            },
            reason=reason,
        )

    def get_guild_voice_regions(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/regions", guild_id=guild_id))

    def get_guild_invites(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/invites", guild_id=guild_id))

    def get_guild_integrations(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/integrations", guild_id=guild_id))

    def delete_guild_integration(
        self, guild_id: Snowflake, integration_id: Snowflake, reason: Optional[str] = None
    ):
        return self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/integrations/{integration_id}",
                guild_id=guild_id,
                integration_id=integration_id,
            ),
            reason=reason,
        )

    def get_guild_widget_settings(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/widget", guild_id=guild_id))

    def modify_guild_widget(
        self,
        guild_id: Snowflake,
        *,
        enabled: UnsetOr[bool] = Unset,
        channel_id: UnsetOr[Optional[Snowflake]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("PATCH", "/guilds/{guild_id}/widget", guild_id=guild_id),
            json_params={"enabled": enabled, "channel_id": channel_id},
            reason=reason,
        )

    def get_guild_widget(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/widget.json", guild_id=guild_id))

    def get_guild_vanity_url(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/vanity-url", guild_id=guild_id))

    def get_guild_widget_image(self, guild_id: Snowflake, *, style: UnsetOr[str] = Unset):
        return self.request(
            Route("GET", "/guilds/{guild_id}/widget.png", guild_id=guild_id),
            query_params={"style": style},
        )

    def get_guild_welcome_screen(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/welcome-screen", guild_id=guild_id))

    def modify_guild_welcome_screen(
        self,
        guild_id: Snowflake,
        *,
        enabled: UnsetOr[Optional[bool]] = Unset,
        welcome_channels: UnsetOr[Optional[list[discord_typings.WelcomeChannelData]]] = Unset,
        description: UnsetOr[Optional[str]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("PATCH", "/guilds/{guild_id}/welcome-screen", guild_id=guild_id),
            json_params={
                "enabled": enabled,
                "welcome_channels": welcome_channels,
                "description": description,
            },
            reason=reason,
        )

    def modify_current_user_voice_state(
        self,
        guild_id: Snowflake,
        *,
        channel_id: UnsetOr[Snowflake] = Unset,
        suppress: UnsetOr[bool] = Unset,
        request_to_speak_timestamp: UnsetOr[Optional[str]] = Unset,
    ):
        return self.request(
            Route("PATCH", "/guilds/{guild_id}/voice-states/@me", guild_id=guild_id),
            json_params={
                "channel_id": channel_id,
                "suppress": suppress,
                "request_to_speak_timestamp": request_to_speak_timestamp,
            },
        )

    def modify_user_voice_state(
        self,
        guild_id: Snowflake,
        user_id: Snowflake,
        *,
        channel_id: Snowflake,
        suppress: UnsetOr[bool] = Unset,
    ):
        return self.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/voice-states/{user_id}",
                guild_id=guild_id,
                user_id=user_id,
            ),
            json_params={"channel_id": channel_id, "suppress": suppress},
        )
