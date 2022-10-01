# SPDX-License-Identifier: MIT

__title__ = "DisCatCore"
__author__ = "EmreTech"
__version__ = "0.1.0"
__license__ = "MIT"

# I have no idea how to prevent this type error
from . import types, utils  # type: ignore
from .dispatcher import *
from .errors import *
from .file import *
from .gateway import *
from .http import *
