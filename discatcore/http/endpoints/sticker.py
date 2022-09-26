# SPDX-License-Identifier: MIT

# this file was auto-generated by scripts/generate_endpoints.py

from typing import Optional

from discord_typings import Snowflake

from ...file import BasicFile
from ...types import Unset
from ..route import Route
from .core import EndpointMixin

__all__ = ("StickerEndpoints",)


class StickerEndpoints(EndpointMixin):
    def get_sticker(self, sticker_id: Snowflake):
        return self.request(Route("GET", "/stickers/{sticker_id}", sticker_id=sticker_id))

    def list_nitro_sticker_packs(self):
        return self.request(Route("GET", "/sticker-packs"))

    def list_guild_stickers(self, guild_id: Snowflake):
        return self.request(Route("GET", "/guilds/{guild_id}/stickers", guild_id=guild_id))

    def get_guild_sticker(self, guild_id: Snowflake, sticker_id: Snowflake):
        return self.request(
            Route(
                "GET",
                "/guilds/{guild_id}/stickers/{sticker_id}",
                guild_id=guild_id,
                sticker_id=sticker_id,
            )
        )

    def create_guild_sticker(
        self, guild_id: Snowflake, *, name: str, description: str = "", tags: str, file: BasicFile
    ):
        from aiohttp import FormData

        form_data = FormData()
        form_data.add_field("name", name)
        form_data.add_field("description", description)
        form_data.add_field("tags", tags)
        form_data.add_field("file", file.fp, content_type=file.content_type)
        return self.request(
            Route("POST", "/guilds/{guild_id}/stickers", guild_id=guild_id), data=form_data
        )

    def modify_guild_sticker(
        self,
        guild_id: Snowflake,
        sticker_id: Snowflake,
        *,
        name: str = Unset,
        description: Optional[str] = Unset,
        tags: str = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route(
                "PATCH",
                "/guilds/{guild_id}/stickers/{sticker_id}",
                guild_id=guild_id,
                sticker_id=sticker_id,
            ),
            json_params={"name": name, "description": description, "tags": tags},
            reason=reason,
        )

    def delete_guild_sticker(
        self, guild_id: Snowflake, sticker_id: Snowflake, reason: Optional[str] = None
    ):
        return self.request(
            Route(
                "DELETE",
                "/guilds/{guild_id}/stickers/{sticker_id}",
                guild_id=guild_id,
                sticker_id=sticker_id,
            ),
            reason=reason,
        )
