# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.request.HTTPRequest`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""

try:
    from typing import Dict, Tuple
except ImportError:
    pass


class HTTPRequest:
    """
    Incoming request, constructed from raw incoming bytes.
    It is passed as first argument to route handlers.
    """

    method: str
    """Request method e.g. "GET" or "POST"."""

    path: str
    """Path of the request."""

    query_params: Dict[str, str]
    """
    Query/GET parameters in the request.

    Example::

            request  = HTTPRequest(raw_request=b"GET /?foo=bar HTTP/1.1...")
            request.query_params
            # {"foo": "bar"}
    """

    http_version: str
    """HTTP version, e.g. "HTTP/1.1"."""

    headers: Dict[str, str]
    """
    Headers from the request as `dict`.

    Values should be accessed using **lower case header names**.

    Example::

            request.headers
            # {'connection': 'keep-alive', 'content-length': '64' ...}
            request.headers["content-length"]
            # '64'
            request.headers["Content-Length"]
            # KeyError: 'Content-Length'
    """

    raw_request: bytes
    """Raw bytes passed to the constructor."""

    def __init__(self, raw_request: bytes = None) -> None:
        self.raw_request = raw_request

        if raw_request is None:
            raise ValueError("raw_request cannot be None")

        header_bytes = self.header_body_bytes[0]

        try:
            (
                self.method,
                self.path,
                self.query_params,
                self.http_version,
            ) = self._parse_start_line(header_bytes)
            self.headers = self._parse_headers(header_bytes)
        except Exception as error:
            raise ValueError("Unparseable raw_request: ", raw_request) from error

    @property
    def body(self) -> bytes:
        """Body of the request, as bytes."""
        return self.header_body_bytes[1]

    @body.setter
    def body(self, body: bytes) -> None:
        self.raw_request = self.header_body_bytes[0] + b"\r\n\r\n" + body

    @property
    def header_body_bytes(self) -> Tuple[bytes, bytes]:
        """Return tuple of header and body bytes."""

        empty_line_index = self.raw_request.find(b"\r\n\r\n")
        header_bytes = self.raw_request[:empty_line_index]
        body_bytes = self.raw_request[empty_line_index + 4 :]

        return header_bytes, body_bytes

    @staticmethod
    def _parse_start_line(header_bytes: bytes) -> Tuple[str, str, Dict[str, str], str]:
        """Parse HTTP Start line to method, path, query_params and http_version."""

        start_line = header_bytes.decode("utf8").splitlines()[0]

        method, path, http_version = start_line.split()

        if "?" not in path:
            path += "?"

        path, query_string = path.split("?", 1)

        query_params = {}
        for query_param in query_string.split("&"):
            if "=" in query_param:
                key, value = query_param.split("=", 1)
                query_params[key] = value
            else:
                query_params[query_param] = ""

        return method, path, query_params, http_version

    @staticmethod
    def _parse_headers(header_bytes: bytes) -> Dict[str, str]:
        """Parse HTTP headers from raw request."""
        header_lines = header_bytes.decode("utf8").splitlines()[1:]

        return {
            name.lower(): value
            for header_line in header_lines
            for name, value in [header_line.split(": ", 1)]
        }
