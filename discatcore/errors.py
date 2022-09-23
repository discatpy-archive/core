"""
The MIT License (MIT)

Copyright (c) 2022-present EmreTech

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from typing import Optional, Union

from aiohttp import ClientResponse
from discord_typings import HTTPErrorResponseData, NestedHTTPErrorsData

__all__ = (
    "DisCatCoreException",
    "HTTPException",
    "UnsupportedAPIVersionWarning",
)


class DisCatCoreException(Exception):
    """Basis for all exceptions in DisCatPy. If you wanted to catch any exception
    thrown by DisCatPy, you would catch this exception.
    """

    pass


def _shorten_error_dict(d: NestedHTTPErrorsData, parent_key: str = ""):
    ret_items: dict[str, str] = {}

    _errors = d.get("_errors")
    if _errors is not None and isinstance(_errors, list):
        ret_items[parent_key] = ", ".join([msg["message"] for msg in _errors])
    else:
        for key, value in d.items():
            key_path = f"{parent_key}.{key}" if parent_key else key
            # pyright thinks the type of value could be object which violates the first parameter
            # of this function
            ret_items.update([(k, v) for k, v in _shorten_error_dict(value, key_path).items()])  # type: ignore

    return ret_items


class HTTPException(DisCatCoreException):
    """Represents an error while attempting to connect to the Discord REST API.

    Args:
        response (aiohttp.ClientResponse): The response from the attempted REST API request.
        data (Union[discord_typings.HTTPErrorResponseData, str, None]): The raw data retrieved from the response.

    Attributes:
        text (str): The error text. Might be empty.
        code (int): The Discord specfic error code of the request.
    """

    __slots__ = ("text", "code")

    def __init__(self, response: ClientResponse, data: Optional[Union[HTTPErrorResponseData, str]]):

        if isinstance(data, dict):
            self.code = data.get("code", 0)
            base = data.get("message", "")
            errors = data.get("errors")
            if errors:
                errors = _shorten_error_dict(errors)
                helpful_msg = "In {0}: {0}".format(t for t in errors.items())
                self.text = f"{base}\n{helpful_msg}"
            else:
                self.text = base
        else:
            self.text = data or ""
            self.code = 0

        format = "{0} {1} (error code: {2}"
        if self.text:
            format += ": {3}"

        format += ")"

        # more shitty aiohttp typing
        super().__init__(format.format(response.status, response.reason, self.code, self.text))  # type: ignore


class BucketMigrated(DisCatCoreException):
    """Represents an internal exception for when a bucket migrates."""

    def __init__(self, discord_hash: str):
        super().__init__(f"This bucket has been migrated to a bucket located at {discord_hash}")


class UnsupportedAPIVersionWarning(Warning):
    """Represents a warning for unsupported API versions."""

    pass


class GatewayReconnect(DisCatCoreException):
    """Represents an exception signaling that the Gateway needs to be reconnected.

    Args:
        url (str): The url to reconnect with. This will be set to the normal gateway url if we cannot resume.
        resume (bool): Whether we can resume or not.

    Attributes:
        url (str): The url to reconnect with. This will be set to the normal gateway url if we cannot resume.
        resume (bool): Whether we can resume or not.
    """

    __slots__ = ("url", "resume")

    def __init__(self, url: str, resume: bool):
        self.url = url
        self.resume = resume

        super().__init__(f"The Gateway should be reconnected to with url {self.url}.")
