# SPDX-License-Identifier: MIT

import io

from discatcore import BasicFile


class TestBasicFile:
    def test_explicit_spoiler(self):
        buffer = io.StringIO("hello there :D")
        file = BasicFile(buffer, "text/plain", filename="hello.txt", spoiler=True)
        assert file.spoiler

    def test_implicit_spoiler(self):
        buffer = io.StringIO("hello there :D")
        file = BasicFile(buffer, "text/plain", filename="SPOILER_hello.txt")
        assert file.spoiler
