# SPDX-License-Identifier: MIT

from typing import Any, Optional, TypedDict

__all__ = ("GatewayPayload",)


class GatewayPayload(TypedDict):
    op: int
    d: Optional[Any]
    s: Optional[int]
    t: Optional[str]
