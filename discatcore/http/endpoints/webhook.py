# SPDX-License-Identifier: MIT

# this file was auto-generated by scripts/generate_endpoints.py

from typing import Optional

import discord_typings
from discord_typings import Snowflake

from ...file import BasicFile
from ...types import Unset, UnsetOr
from ..route import Route
from .core import EndpointMixin

__all__ = ("WebhookEndpoints",)


class WebhookEndpoints(EndpointMixin):
    def create_webhook(
        self,
        channel_id: Snowflake,
        *,
        name: str,
        avatar: UnsetOr[Optional[str]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("POST", "/channels/{channel_id}/webhooks", channel_id=channel_id),
            json_params={"name": name, "avatar": avatar},
            reason=reason,
        )

    def get_channel_webhooks(self, channel_id: Snowflake):
        return self.request(Route("GET", "/channels/{channel_id}/webhooks", channel_id=channel_id))

    def get_guild_webhooks(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/webhooks", guild_id=guild_id))

    def get_webhook(self, webhook_id: Snowflake):
        return self.request(Route("GET", "/webhooks/{webhook_id}", webhook_id=webhook_id))

    def get_webhook_with_token(self, webhook_id: Snowflake, webhook_token: str):
        return self.request(
            Route(
                "GET",
                "/webhooks/{webhook_id}/{webhook_token}",
                webhook_id=webhook_id,
                webhook_token=webhook_token,
            )
        )

    def modify_webhook(
        self,
        webhook_id: Snowflake,
        *,
        name: UnsetOr[str] = Unset,
        avatar: UnsetOr[Optional[str]] = Unset,
        channel_id: UnsetOr[Snowflake] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("PATCH", "/webhooks/{webhook_id}", webhook_id=webhook_id),
            json_params={"name": name, "avatar": avatar, "channel_id": channel_id},
            reason=reason,
        )

    def modify_webhook_with_token(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        name: UnsetOr[str] = Unset,
        avatar: UnsetOr[Optional[str]] = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route(
                "PATCH",
                "/webhooks/{webhook_id}/{webhook_token}",
                webhook_id=webhook_id,
                webhook_token=webhook_token,
            ),
            json_params={"name": name, "avatar": avatar},
            reason=reason,
        )

    def delete_webhook(self, webhook_id: Snowflake, reason: Optional[str] = None):
        return self.request(
            Route("DELETE", "/webhooks/{webhook_id}", webhook_id=webhook_id), reason=reason
        )

    def delete_webhook_with_token(
        self, webhook_id: Snowflake, webhook_token: str, reason: Optional[str] = None
    ):
        return self.request(
            Route(
                "DELETE",
                "/webhooks/{webhook_id}/{webhook_token}",
                webhook_id=webhook_id,
                webhook_token=webhook_token,
            ),
            reason=reason,
        )

    def execute_webhook(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        *,
        content: UnsetOr[str] = Unset,
        username: UnsetOr[str] = Unset,
        avatar_url: UnsetOr[str] = Unset,
        tts: UnsetOr[bool] = Unset,
        embeds: UnsetOr[list[discord_typings.EmbedData]] = Unset,
        allowed_mentions: UnsetOr[discord_typings.AllowedMentionsData] = Unset,
        components: UnsetOr[list[discord_typings.ComponentData]] = Unset,
        attachments: UnsetOr[list[discord_typings.PartialAttachmentData]] = Unset,
        flags: UnsetOr[int] = Unset,
        thread_name: UnsetOr[str] = Unset,
        wait: bool = False,
        thread_id: UnsetOr[Snowflake] = Unset,
        files: UnsetOr[list[BasicFile]] = Unset,
    ):
        return self.request(
            Route(
                "POST",
                "/webhooks/{webhook_id}/{webhook_token}",
                webhook_id=webhook_id,
                webhook_token=webhook_token,
            ),
            json_params={
                "content": content,
                "username": username,
                "avatar_url": avatar_url,
                "tts": tts,
                "embeds": embeds,
                "allowed_mentions": allowed_mentions,
                "components": components,
                "attachments": attachments,
                "flags": flags,
                "thread_name": thread_name,
            },
            query_params={"wait": wait, "thread_id": thread_id},
            files=files,
        )

    def get_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: UnsetOr[Snowflake] = Unset,
    ):
        return self.request(
            Route(
                "GET",
                "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
                webhook_id=webhook_id,
                webhook_token=webhook_token,
                message_id=message_id,
            ),
            query_params={"thread_id": thread_id},
        )

    def edit_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        content: UnsetOr[Optional[str]] = Unset,
        embeds: UnsetOr[Optional[list[discord_typings.EmbedData]]] = Unset,
        allowed_mentions: UnsetOr[Optional[discord_typings.AllowedMentionsData]] = Unset,
        components: UnsetOr[Optional[list[discord_typings.ComponentData]]] = Unset,
        attachments: UnsetOr[Optional[list[discord_typings.PartialAttachmentData]]] = Unset,
        thread_id: UnsetOr[Snowflake] = Unset,
        files: UnsetOr[list[BasicFile]] = Unset,
    ):
        return self.request(
            Route(
                "PATCH",
                "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
                webhook_id=webhook_id,
                webhook_token=webhook_token,
                message_id=message_id,
            ),
            json_params={
                "content": content,
                "embeds": embeds,
                "allowed_mentions": allowed_mentions,
                "components": components,
                "attachments": attachments,
            },
            query_params={"thread_id": thread_id},
            files=files,
        )

    def delete_webhook_message(
        self,
        webhook_id: Snowflake,
        webhook_token: str,
        message_id: Snowflake,
        *,
        thread_id: UnsetOr[Snowflake] = Unset,
    ):
        return self.request(
            Route(
                "DELETE",
                "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
                webhook_id=webhook_id,
                webhook_token=webhook_token,
                message_id=message_id,
            ),
            query_params={"thread_id": thread_id},
        )
