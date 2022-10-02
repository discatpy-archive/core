# SPDX-License-Identifier: MIT

__title__ = "DisCatCore"
__author__ = "EmreTech"
__version__ = "0.1.0"
__license__ = "MIT"

from . import gateway, http, types, utils
from .errors import *
from .file import *
from .impl import Dispatcher, Event

# TODO: make a script to automatically generate this
__all__ = (
    # errors.py
    "DisCatCoreException",
    "HTTPException",
    "BucketMigrated",
    "UnsupportedAPIVersionWarning",
    "GatewayReconnect",
    # file.py
    "BasicFile",
    # misc
    "gateway",
    "http",
    "types",
    "utils",
    "Dispatcher",
    "Event",
)
