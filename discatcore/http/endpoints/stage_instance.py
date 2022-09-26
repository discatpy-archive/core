# SPDX-License-Identifier: MIT

# this file was auto-generated by scripts/generate_endpoints.py

from typing import Optional

from discord_typings import Snowflake

from ...types import Unset
from ..route import Route
from .core import EndpointMixin

__all__ = ("StageInstanceEndpoints",)


class StageInstanceEndpoints(EndpointMixin):
    def create_stage_instance(
        self,
        *,
        channel_id: Snowflake,
        topic: str,
        privacy_level: int = Unset,
        send_start_notification: bool = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("POST", "/stage-instances"),
            json_params={
                "channel_id": channel_id,
                "topic": topic,
                "privacy_level": privacy_level,
                "send_start_notification": send_start_notification,
            },
            reason=reason,
        )

    def get_stage_instance(self, channel_id: Snowflake):
        return self.request(Route("GET", "/stage-instances/{channel_id}", channel_id=channel_id))

    def modify_stage_instance(
        self,
        channel_id: Snowflake,
        *,
        topic: str = Unset,
        privacy_level: int = Unset,
        reason: Optional[str] = None,
    ):
        return self.request(
            Route("PATCH", "/stage-instances/{channel_id}", channel_id=channel_id),
            json_params={"topic": topic, "privacy_level": privacy_level},
            reason=reason,
        )

    def delete_stage_instance(self, channel_id: Snowflake, reason: Optional[str] = None):
        return self.request(
            Route("DELETE", "/stage-instances/{channel_id}", channel_id=channel_id), reason=reason
        )
