# SPDX-License-Identifier: MIT

# this file was auto-generated by scripts/generate_endpoints.py

import typing as t

import discord_typings as dt

from ...file import BasicFile
from ...types import Unset, UnsetOr
from ..route import Route
from .core import EndpointMixin

__all__ = ("WebhookEndpoints",)


class WebhookEndpoints(EndpointMixin):
    def create_webhook(
        self,
        channel_id: dt.Snowflake,
        *,
        name: str,
        avatar: UnsetOr[t.Optional[str]] = Unset,
        reason: t.Optional[str] = None,
    ):
        return self.request(
            Route("POST", "/channels/{channel_id}/webhooks", channel_id=channel_id),
            json_params={"name": name, "avatar": avatar},
            reason=reason,
        )

    def get_channel_webhooks(self, channel_id: dt.Snowflake):
        return self.request(Route("GET", "/channels/{channel_id}/webhooks", channel_id=channel_id))

    def get_guild_webhooks(self, guild_id: dt.Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/webhooks", guild_id=guild_id))

    def get_webhook(self, webhook_id: dt.Snowflake):
        return self.request(Route("GET", "/webhooks/{webhook_id}", webhook_id=webhook_id))

    def get_webhook_with_token(self, webhook_id: dt.Snowflake, webhook_token: str):
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
        webhook_id: dt.Snowflake,
        *,
        name: UnsetOr[str] = Unset,
        avatar: UnsetOr[t.Optional[str]] = Unset,
        channel_id: UnsetOr[dt.Snowflake] = Unset,
        reason: t.Optional[str] = None,
    ):
        return self.request(
            Route("PATCH", "/webhooks/{webhook_id}", webhook_id=webhook_id),
            json_params={"name": name, "avatar": avatar, "channel_id": channel_id},
            reason=reason,
        )

    def modify_webhook_with_token(
        self,
        webhook_id: dt.Snowflake,
        webhook_token: str,
        *,
        name: UnsetOr[str] = Unset,
        avatar: UnsetOr[t.Optional[str]] = Unset,
        reason: t.Optional[str] = None,
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

    def delete_webhook(self, webhook_id: dt.Snowflake, reason: t.Optional[str] = None):
        return self.request(
            Route("DELETE", "/webhooks/{webhook_id}", webhook_id=webhook_id), reason=reason
        )

    def delete_webhook_with_token(
        self, webhook_id: dt.Snowflake, webhook_token: str, reason: t.Optional[str] = None
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
        webhook_id: dt.Snowflake,
        webhook_token: str,
        *,
        content: UnsetOr[str] = Unset,
        username: UnsetOr[str] = Unset,
        avatar_url: UnsetOr[str] = Unset,
        tts: UnsetOr[bool] = Unset,
        embeds: UnsetOr[list[dt.EmbedData]] = Unset,
        allowed_mentions: UnsetOr[dt.AllowedMentionsData] = Unset,
        components: UnsetOr[list[dt.ComponentData]] = Unset,
        attachments: UnsetOr[list[dt.PartialAttachmentData]] = Unset,
        flags: UnsetOr[int] = Unset,
        thread_name: UnsetOr[str] = Unset,
        wait: bool = False,
        thread_id: UnsetOr[dt.Snowflake] = Unset,
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
        webhook_id: dt.Snowflake,
        webhook_token: str,
        message_id: dt.Snowflake,
        *,
        thread_id: UnsetOr[dt.Snowflake] = Unset,
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
        webhook_id: dt.Snowflake,
        webhook_token: str,
        message_id: dt.Snowflake,
        *,
        content: UnsetOr[t.Optional[str]] = Unset,
        embeds: UnsetOr[t.Optional[list[dt.EmbedData]]] = Unset,
        allowed_mentions: UnsetOr[t.Optional[dt.AllowedMentionsData]] = Unset,
        components: UnsetOr[t.Optional[list[dt.ComponentData]]] = Unset,
        attachments: UnsetOr[t.Optional[list[dt.PartialAttachmentData]]] = Unset,
        thread_id: UnsetOr[dt.Snowflake] = Unset,
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
        webhook_id: dt.Snowflake,
        webhook_token: str,
        message_id: dt.Snowflake,
        *,
        thread_id: UnsetOr[dt.Snowflake] = Unset,
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
