# SPDX-License-Identifier: MIT

__title__ = "DisCatCore"
__author__ = "EmreTech"
__version__ = "0.1.0"
__license__ = "MIT"

from typing import Literal, NamedTuple

from . import gateway, http, types, utils
from .errors import *
from .file import *
from .impl import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    patch: int
    release_level: Literal["alpha", "beta", "candidate", "final"]
    build_metadata: int


version_info: VersionInfo = VersionInfo(
    major=0, minor=2, patch=0, release_level="alpha", build_metadata=0
)

__all__ = (
    "gateway",
    "http",
    "types",
    "utils",
    "VersionInfo",
    "version_info",
)
__all__ += errors.__all__
__all__ += file.__all__
__all__ += impl.__all__
