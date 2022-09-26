# SPDX-License-Identifier: MIT

# this file was auto-generated by scripts/generate_endpoints.py

from typing import Any, Optional, Union

import discord_typings
from discord_typings import Snowflake

from discatcore.file import BasicFile
from discatcore.http.endpoints.core import EndpointMixin
from discatcore.http.route import Route
from discatcore.types import Unset

__all__ = ("ApplicationCommandEndpoints",)


class ApplicationCommandEndpoints(EndpointMixin):
    def get_global_application_commands(
        self, application_id: Snowflake, *, with_localizations: bool = Unset
    ):
        return self.request(
            Route("GET", "/applications/{application_id}/commands", application_id=application_id),
            query_params={"with_localizations": with_localizations},
        )

    def create_global_application_command(
        self,
        application_id: Snowflake,
        *,
        name: str,
        name_localizations: Optional[dict[discord_typings.Locales, str]] = Unset,
        description: str,
        description_localizations: Optional[dict[discord_typings.Locales, str]] = Unset,
        options: list[discord_typings.ApplicationCommandOptionData] = Unset,
        default_member_permissions: Optional[str] = Unset,
        dm_permission: Optional[bool] = Unset,
        type: discord_typings.ApplicationCommandTypes = 1,
    ):
        return self.request(
            Route("POST", "/applications/{application_id}/commands", application_id=application_id),
            json_params={
                "name": name,
                "name_localizations": name_localizations,
                "description": description,
                "description_localizations": description_localizations,
                "options": options,
                "default_member_permissions": default_member_permissions,
                "dm_permission": dm_permission,
                "type": type,
            },
        )

    def get_global_application_command(self, application_id: Snowflake, command_id: Snowflake):
        return self.request(
            Route(
                "GET",
                "/applications/{application_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
            )
        )

    def edit_global_application_command(
        self,
        application_id: Snowflake,
        command_id: Snowflake,
        *,
        name: str = Unset,
        name_localizations: Optional[dict[discord_typings.Locales, str]] = Unset,
        description: str = Unset,
        description_localizations: Optional[dict[discord_typings.Locales, str]] = Unset,
        options: list[discord_typings.ApplicationCommandOptionData] = Unset,
        default_member_permissions: Optional[str] = Unset,
        dm_permission: Optional[bool] = Unset,
    ):
        return self.request(
            Route(
                "PATCH",
                "/applications/{application_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
            ),
            json_params={
                "name": name,
                "name_localizations": name_localizations,
                "description": description,
                "description_localizations": description_localizations,
                "options": options,
                "default_member_permissions": default_member_permissions,
                "dm_permission": dm_permission,
            },
        )

    def delete_global_application_command(self, application_id: Snowflake, command_id: Snowflake):
        return self.request(
            Route(
                "DELETE",
                "/applications/{application_id}/commands/{command_id}",
                application_id=application_id,
                command_id=command_id,
            )
        )

    def bulk_overwrite_global_application_commands(
        self, application_id: Snowflake, *, commands: list[discord_typings.ApplicationCommandData]
    ):
        return self.request(
            Route("PUT", "/applications/{application_id}/commands", application_id=application_id),
            json_params=commands,
        )

    def get_guild_application_commands(
        self, application_id: Snowflake, guild_id: Snowflake, *, with_localizations: bool = Unset
    ):
        return self.request(
            Route(
                "GET",
                "/applications/{application_id}/guilds/{guild_id}/commands",
                application_id=application_id,
                guild_id=guild_id,
            ),
            query_params={"with_localizations": with_localizations},
        )

    def create_guild_application_command(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        *,
        name: str,
        name_localizations: Optional[dict[discord_typings.Locales, str]] = Unset,
        description: str,
        description_localizations: Optional[dict[discord_typings.Locales, str]] = Unset,
        options: list[discord_typings.ApplicationCommandOptionData] = Unset,
        default_member_permissions: Optional[str] = Unset,
        dm_permission: Optional[bool] = Unset,
        type: discord_typings.ApplicationCommandTypes = 1,
    ):
        return self.request(
            Route(
                "POST",
                "/applications/{application_id}/guilds/{guild_id}/commands",
                application_id=application_id,
                guild_id=guild_id,
            ),
            json_params={
                "name": name,
                "name_localizations": name_localizations,
                "description": description,
                "description_localizations": description_localizations,
                "options": options,
                "default_member_permissions": default_member_permissions,
                "dm_permission": dm_permission,
                "type": type,
            },
        )

    def get_guild_application_command(
        self, application_id: Snowflake, guild_id: Snowflake, command_id: Snowflake
    ):
        return self.request(
            Route(
                "GET",
                "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                application_id=application_id,
                guild_id=guild_id,
                command_id=command_id,
            )
        )

    def edit_guild_application_command(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        command_id: Snowflake,
        *,
        name: str = Unset,
        name_localizations: Optional[dict[discord_typings.Locales, str]] = Unset,
        description: str = Unset,
        description_localizations: Optional[dict[discord_typings.Locales, str]] = Unset,
        options: list[discord_typings.ApplicationCommandOptionData] = Unset,
        default_member_permissions: Optional[str] = Unset,
        dm_permission: Optional[bool] = Unset,
    ):
        return self.request(
            Route(
                "PATCH",
                "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                application_id=application_id,
                guild_id=guild_id,
                command_id=command_id,
            ),
            json_params={
                "name": name,
                "name_localizations": name_localizations,
                "description": description,
                "description_localizations": description_localizations,
                "options": options,
                "default_member_permissions": default_member_permissions,
                "dm_permission": dm_permission,
            },
        )

    def delete_guild_application_command(
        self, application_id: Snowflake, guild_id: Snowflake, command_id: Snowflake
    ):
        return self.request(
            Route(
                "DELETE",
                "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
                application_id=application_id,
                guild_id=guild_id,
                command_id=command_id,
            )
        )

    def bulk_overwrite_guild_application_commands(
        self,
        application_id: Snowflake,
        guild_id: Snowflake,
        *,
        commands: list[discord_typings.ApplicationCommandData],
    ):
        return self.request(
            Route(
                "PUT",
                "/applications/{application_id}/guilds/{guild_id}/commands",
                application_id=application_id,
                guild_id=guild_id,
            ),
            json_params=commands,
        )

    def get_guild_application_command_permissions(
        self, application_id: Snowflake, guild_id: Snowflake
    ):
        return self.request(
            Route(
                "GET",
                "/applications/{application_id}/guilds/{guild_id}/commands/permissions",
                application_id=application_id,
                guild_id=guild_id,
            )
        )

    def get_application_command_permissions(
        self, application_id: Snowflake, guild_id: Snowflake, command_id: Snowflake
    ):
        return self.request(
            Route(
                "GET",
                "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions",
                application_id=application_id,
                guild_id=guild_id,
                command_id=command_id,
            )
        )