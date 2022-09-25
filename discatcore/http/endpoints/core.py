# SPDX-License-Identifier: MIT

from typing import Any, Optional, Union

from discatcore.file import BasicFile
from discatcore.http.route import Route
from discatcore.types import Unset

__all__ = ("EndpointMixin",)


class EndpointMixin:
    async def request(
        self,
        route: Route,
        *,
        query_params: Optional[dict[str, Any]] = None,
        json_params: dict[str, Any] = Unset,
        reason: Optional[str] = None,
        files: list[BasicFile] = Unset,
        **extras: Any,
    ) -> Union[Any, str]:
        pass
