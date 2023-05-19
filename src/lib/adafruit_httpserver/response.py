# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.response.HTTPResponse`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""

try:
    from typing import Optional, Dict, Union, Tuple, Callable
    from socket import socket
    from socketpool import SocketPool
except ImportError:
    pass

import os
from errno import EAGAIN, ECONNRESET

from .exceptions import (
    BackslashInPathError,
    FileNotExistsError,
    ParentDirectoryReferenceError,
    ResponseAlreadySentError,
)
from .mime_type import MIMEType
from .request import HTTPRequest
from .status import HTTPStatus, CommonHTTPStatus
from .headers import HTTPHeaders


def _prevent_multiple_send_calls(function: Callable):
    """
    Decorator that prevents calling ``send`` or ``send_file`` more than once.
    """

    def wrapper(self: "HTTPResponse", *args, **kwargs):
        if self._response_already_sent:  # pylint: disable=protected-access
            raise ResponseAlreadySentError

        result = function(self, *args, **kwargs)
        return result

    return wrapper


class HTTPResponse:
    """
    Response to a given `HTTPRequest`. Use in `HTTPServer.route` decorator functions.

    Example::

        # Response with 'Content-Length' header
        @server.route(path, method)
        def route_func(request):

            response = HTTPResponse(request)
            response.send("Some content", content_type="text/plain")

            # or

            response = HTTPResponse(request)
            with response:
                response.send(body='Some content', content_type="text/plain")

            # or

            with HTTPResponse(request) as response:
                response.send("Some content", content_type="text/plain")

        # Response with 'Transfer-Encoding: chunked' header
        @server.route(path, method)
        def route_func(request):

            response = HTTPResponse(request, content_type="text/plain", chunked=True)
            with response:
                response.send_chunk("Some content")
                response.send_chunk("Some more content")

            # or

            with HTTPResponse(request, content_type="text/plain", chunked=True) as response:
                response.send_chunk("Some content")
                response.send_chunk("Some more content")
    """

    request: HTTPRequest
    """The request that this is a response to."""

    http_version: str
    status: HTTPStatus
    headers: HTTPHeaders
    content_type: str
    """
    Defaults to ``text/plain`` if not set.

    Can be explicitly provided in the constructor, in ``send()`` or
    implicitly determined from filename in ``send_file()``.

    Common MIME types are defined in `adafruit_httpserver.mime_type.MIMEType`.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        request: HTTPRequest,
        status: Union[HTTPStatus, Tuple[int, str]] = CommonHTTPStatus.OK_200,
        headers: Union[HTTPHeaders, Dict[str, str]] = None,
        content_type: str = None,
        http_version: str = "HTTP/1.1",
        chunked: bool = False,
    ) -> None:
        """
        Creates an HTTP response.

        Sets `status`, ``headers`` and `http_version`
        and optionally default ``content_type``.

        To send the response, call ``send`` or ``send_file``.
        For chunked response use
        ``with HTTPRequest(request, content_type=..., chunked=True) as r:`` and `send_chunk`.
        """
        self.request = request
        self.status = status if isinstance(status, HTTPStatus) else HTTPStatus(*status)
        self.headers = (
            headers.copy() if isinstance(headers, HTTPHeaders) else HTTPHeaders(headers)
        )
        self.content_type = content_type
        self.http_version = http_version
        self.chunked = chunked
        self._response_already_sent = False

    def _send_headers(
        self,
        content_length: Optional[int] = None,
        content_type: str = None,
    ) -> None:
        """
        Sends headers.
        Implicitly called by ``send`` and ``send_file`` and in
        ``with HTTPResponse(request, chunked=True) as response:`` context manager.
        """
        headers = self.headers.copy()

        response_message_header = (
            f"{self.http_version} {self.status.code} {self.status.text}\r\n"
        )

        headers.setdefault(
            "Content-Type", content_type or self.content_type or MIMEType.TYPE_TXT
        )
        headers.setdefault("Connection", "close")
        if self.chunked:
            headers.setdefault("Transfer-Encoding", "chunked")
        else:
            headers.setdefault("Content-Length", content_length)

        for header, value in headers.items():
            response_message_header += f"{header}: {value}\r\n"
        response_message_header += "\r\n"

        self._send_bytes(
            self.request.connection, response_message_header.encode("utf-8")
        )

    @_prevent_multiple_send_calls
    def send(
        self,
        body: str = "",
        content_type: str = None,
    ) -> None:
        """
        Sends response with content built from ``body``.
        Implicitly calls ``_send_headers`` before sending the body.

        Should be called **only once** per response.
        """

        if getattr(body, "encode", None):
            encoded_response_message_body = body.encode("utf-8")
        else:
            encoded_response_message_body = body

        self._send_headers(
            content_type=content_type or self.content_type,
            content_length=len(encoded_response_message_body),
        )
        self._send_bytes(self.request.connection, encoded_response_message_body)
        self._response_already_sent = True

    @staticmethod
    def _check_file_path_is_valid(file_path: str) -> bool:
        """
        Checks if ``file_path`` is valid.
        If not raises error corresponding to the problem.
        """

        # Check for backslashes
        if "\\" in file_path:  # pylint: disable=anomalous-backslash-in-string
            raise BackslashInPathError(file_path)

        # Check each component of the path for parent directory references
        for part in file_path.split("/"):
            if part == "..":
                raise ParentDirectoryReferenceError(file_path)

    @staticmethod
    def _get_file_length(file_path: str) -> int:
        """
        Tries to get the length of the file at ``file_path``.
        Raises ``FileNotExistsError`` if file does not exist.
        """
        try:
            return os.stat(file_path)[6]
        except OSError:
            raise FileNotExistsError(file_path)  # pylint: disable=raise-missing-from

    @_prevent_multiple_send_calls
    def send_file(  # pylint: disable=too-many-arguments
        self,
        filename: str = "index.html",
        root_path: str = "./",
        buffer_size: int = 1024,
        head_only: bool = False,
        safe: bool = True,
    ) -> None:
        """
        Send response with content of ``filename`` located in ``root_path``.
        Implicitly calls ``_send_headers`` before sending the file content.
        File is send split into ``buffer_size`` parts.

        Should be called **only once** per response.
        """

        if safe:
            self._check_file_path_is_valid(filename)

        if not root_path.endswith("/"):
            root_path += "/"
        if filename.startswith("/"):
            filename = filename[1:]

        full_file_path = root_path + filename

        file_length = self._get_file_length(full_file_path)

        self._send_headers(
            content_type=MIMEType.from_file_name(filename),
            content_length=file_length,
        )

        if not head_only:
            with open(full_file_path, "rb") as file:
                while bytes_read := file.read(buffer_size):
                    self._send_bytes(self.request.connection, bytes_read)
        self._response_already_sent = True

    def send_chunk(self, chunk: str = "") -> None:
        """
        Sends chunk of response.

        Should be used **only** inside
        ``with HTTPResponse(request, chunked=True) as response:`` context manager.

        :param str chunk: String data to be sent.
        """
        if getattr(chunk, "encode", None):
            chunk = chunk.encode("utf-8")

        self._send_bytes(self.request.connection, b"%x\r\n" % len(chunk))
        self._send_bytes(self.request.connection, chunk)
        self._send_bytes(self.request.connection, b"\r\n")

    def __enter__(self):
        if self.chunked:
            self._send_headers()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None:
            return False

        if self.chunked:
            self.send_chunk("")
        return True

    @staticmethod
    def _send_bytes(
        conn: Union["SocketPool.Socket", "socket.socket"],
        buffer: Union[bytes, bytearray, memoryview],
    ):
        bytes_sent = 0
        bytes_to_send = len(buffer)
        view = memoryview(buffer)
        while bytes_sent < bytes_to_send:
            try:
                bytes_sent += conn.send(view[bytes_sent:])
            except OSError as exc:
                if exc.errno == EAGAIN:
                    continue
                if exc.errno == ECONNRESET:
                    return
                raise
