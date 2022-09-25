# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from discord_typings import (
    ApplicationCommandPermissionsUpdateData,
    ChannelCreateData,
    ChannelDeleteData,
    ChannelUpdateEvent,
    EmojiData,
    GuildCreateData,
    GuildDeleteData,
    GuildMemberAddData,
    GuildMemberData,
    GuildMemberUpdateData,
    GuildScheduledEventCreateData,
    GuildScheduledEventDeleteData,
    GuildScheduledEventUpdateData,
    GuildUpdateData,
    IntegrationData,
    InteractionCreateData,
    InviteCreateData,
    MessageCreateData,
    MessageUpdateData,
    PresenceUpdateData,
    RoleData,
    StageInstanceCreateData,
    StageInstanceDeleteData,
    StageInstanceUpdateData,
    StickerData,
    ThreadChannelData,
    ThreadCreateData,
    ThreadDeleteData,
    ThreadMemberData,
    ThreadUpdateData,
    UpdatePresenceData,
    UserData,
    VoiceStateUpdateData,
)

from discatcore.types import Snowflake

if TYPE_CHECKING:
    from discatcore.client import Client

__all__ = ("GatewayEventProtos",)


class GatewayEventProtos:
    """Registers event protos for Gateway events."""

    def __init__(self, client: Client):
        self.client = client

        if not self.client._event_protos_handler_hooked:
            for k in dir(self):
                v = getattr(self, k)
                if not k.startswith("_") and callable(v):
                    self.client.new_event(k).set_proto(v)

            self.client._event_protos_handler_hooked = True

    # Gateway State events

    async def ready(self):
        pass

    async def resumed(self):
        pass

    async def reconnect(self):
        pass

    async def invalid_session(self, reconnect: bool):
        pass

    # Application Command events

    async def application_command_permissions_update(
        self, permissions: ApplicationCommandPermissionsUpdateData
    ):
        pass

    # TODO: Auto Moderation events

    # Channel/Thread events

    async def channel_create(self, channel: ChannelCreateData):
        pass

    async def channel_update(self, channel: ChannelUpdateEvent):
        pass

    async def channel_delete(self, channel: ChannelDeleteData):
        pass

    async def thread_create(self, thread: ThreadCreateData):
        pass

    async def thread_update(self, thread: ThreadUpdateData):
        pass

    async def thread_delete(self, thread: ThreadDeleteData):
        pass

    async def thread_list_sync(
        self,
        guild_id: Snowflake,
        channel_ids: list[Snowflake],
        threads: list[ThreadChannelData],
        members: list[ThreadMemberData],
    ):
        pass

    async def thread_members_update(
        self,
        id: Snowflake,
        guild_id: Snowflake,
        member_count: int,
        added_members: list[ThreadMemberData],
        removed_member_ids: list[Snowflake],
    ):
        pass

    async def channel_pins_update(
        self,
        guild_id: Snowflake,
        channel_id: Snowflake,
        last_pin_timestamp: Optional[datetime],
    ):
        pass

    # Guild events

    async def guild_create(self, guild: GuildCreateData):
        pass

    async def guild_update(self, guild: GuildUpdateData):
        pass

    async def guild_delete(self, guild: GuildDeleteData):
        pass

    async def guild_ban_add(self, guild_id: Snowflake, user: UserData):
        pass

    async def guild_ban_remove(self, guild_id: Snowflake, user: UserData):
        pass

    async def guild_emojis_update(self, guild_id: Snowflake, emojis: list[EmojiData]):
        pass

    async def guild_stickers_update(self, guild_id: Snowflake, stickers: list[StickerData]):
        pass

    async def guild_integrations_update(self, guild_id: Snowflake):
        pass

    async def guild_member_add(self, member: GuildMemberAddData):
        pass

    async def guild_member_remove(self, guild_id: Snowflake, user: UserData):
        pass

    async def guild_member_update(self, member: GuildMemberUpdateData):
        pass

    async def guild_members_chunk(
        self,
        guild_id: Snowflake,
        members: list[GuildMemberData],
        chunk_index: int,
        chunk_count: int,
        not_found: list[Snowflake],
        presences: list[UpdatePresenceData],
        nonce: str,
    ):
        pass

    async def guild_role_create(self, guild_id: Snowflake, role: RoleData):
        pass

    async def guild_role_update(self, guild_id: Snowflake, role: RoleData):
        pass

    async def guild_role_delete(self, guild_id: Snowflake, role_id: Snowflake):
        pass

    async def guild_scheduled_event_create(self, scheduled_event: GuildScheduledEventCreateData):
        pass

    async def guild_scheduled_event_update(self, scheduled_event: GuildScheduledEventUpdateData):
        pass

    async def guild_scheduled_event_delete(self, scheduled_event: GuildScheduledEventDeleteData):
        pass

    async def guild_scheduled_event_user_add(
        self, guild_scheduled_event_id: Snowflake, user_id: Snowflake, guild_id: Snowflake
    ):
        pass

    async def guild_scheduled_event_user_remove(
        self, guild_scheduled_event_id: Snowflake, user_id: Snowflake, guild_id: Snowflake
    ):
        pass

    # Integration events
    # TODO: remove?

    async def integration_create(self, integration: IntegrationData):
        pass

    async def integration_update(self, integration: IntegrationData):
        pass

    async def integration_delete(self, integration: IntegrationData):
        pass

    # Invite events

    async def invite_create(self, invite: InviteCreateData):
        pass

    async def invite_delete(self, channel_id: Snowflake, guild_id: Snowflake, code: str):
        pass

    # Message events

    async def message_create(self, message: MessageCreateData):
        pass

    async def message_update(self, message: MessageUpdateData):
        pass

    async def message_delete(self, id: Snowflake, channel_id: Snowflake, guild_id: Snowflake):
        pass

    async def message_delete_bulk(
        self, ids: list[Snowflake], channel_id: Snowflake, guild_id: Snowflake
    ):
        pass

    async def message_reaction_add(
        self,
        user_id: Snowflake,
        channel_id: Snowflake,
        message_id: Snowflake,
        guild_id: Snowflake,
        member: GuildMemberData,
        emoji: EmojiData,
    ):
        pass

    async def message_reaction_remove(
        self,
        user_id: Snowflake,
        channel_id: Snowflake,
        message_id: Snowflake,
        guild_id: Snowflake,
        emoji: EmojiData,
    ):
        pass

    async def message_reaction_remove_all(
        self, channel_id: Snowflake, message_id: Snowflake, guild_id: Snowflake
    ):
        pass

    async def message_reaction_remove_emoji(
        self,
        channel_id: Snowflake,
        guild_id: Snowflake,
        message_id: Snowflake,
        emoji: EmojiData,
    ):
        pass

    # Presence events

    async def presence_update(self, presence: PresenceUpdateData):
        pass

    async def typing_start(
        self,
        channel_id: Snowflake,
        guild_id: Snowflake,
        user_id: Snowflake,
        timestamp: int,
        member: GuildMemberData,
    ):
        pass

    # User events
    # TODO: remove?

    async def user_update(self, user: UserData):
        pass

    # Voice events

    async def voice_state_update(self, voice_state: VoiceStateUpdateData):
        pass

    async def voice_server_update(self, token: str, guild_id: Snowflake, endpoint: Optional[str]):
        pass

    # Webhook events

    async def webhooks_update(self, guild_id: Snowflake, channel_id: Snowflake):
        pass

    # Interaction events

    async def interaction_create(self, interaction: InteractionCreateData):
        pass

    # Stage Instance events

    async def stage_instance_create(self, stage_instance: StageInstanceCreateData):
        pass

    async def stage_instance_update(self, stage_instance: StageInstanceUpdateData):
        pass

    async def stage_instance_delete(self, stage_instance: StageInstanceDeleteData):
        pass
