# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.route._HTTPRoute`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""

from .methods import HTTPMethod


class _HTTPRoute:
    """Route definition for different paths, see `adafruit_httpserver.server.HTTPServer.route`."""

    def __init__(self, path: str = "", method: HTTPMethod = HTTPMethod.GET) -> None:

        self.path = path
        self.method = method

    def __hash__(self) -> int:
        return hash(self.method) ^ hash(self.path)

    def __eq__(self, other: "_HTTPRoute") -> bool:
        return self.method == other.method and self.path == other.path

    def __repr__(self) -> str:
        return f"HTTPRoute(path={repr(self.path)}, method={repr(self.method)})"
