# SPDX-License-Identifier: MIT

from typing import Any, Optional, Union

from ...file import BasicFile
from ...types import Unset
from ..route import Route

__all__ = ("EndpointMixin",)


class EndpointMixin:
    async def request(
        self,
        route: Route,
        *,
        query_params: Optional[dict[str, Any]] = None,
        json_params: Union[dict[str, Any], list[Any]] = Unset,
        reason: Optional[str] = None,
        files: list[BasicFile] = Unset,
        **extras: Any,
    ) -> Union[Any, str]:
        pass
