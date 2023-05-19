# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.methods.HTTPMethod`
====================================================
* Author(s): Michał Pokusa
"""


class HTTPMethod:  # pylint: disable=too-few-public-methods
    """Enum with HTTP methods."""

    GET = "GET"
    """GET method."""

    POST = "POST"
    """POST method."""

    PUT = "PUT"
    """PUT method"""

    DELETE = "DELETE"
    """DELETE method"""

    PATCH = "PATCH"
    """PATCH method"""

    HEAD = "HEAD"
    """HEAD method"""

    OPTIONS = "OPTIONS"
    """OPTIONS method"""

    TRACE = "TRACE"
    """TRACE method"""

    CONNECT = "CONNECT"
    """CONNECT method"""
