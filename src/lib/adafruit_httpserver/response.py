# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.response`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""

try:
    from typing import Optional, Dict, Union, Tuple, Generator, Any
    from socket import socket
    from socketpool import SocketPool
except ImportError:
    pass

import os
import json
from errno import EAGAIN, ECONNRESET

from .exceptions import (
    BackslashInPathError,
    FileNotExistsError,
    ParentDirectoryReferenceError,
)
from .mime_types import MIMETypes
from .request import Request
from .status import Status, OK_200, TEMPORARY_REDIRECT_307, PERMANENT_REDIRECT_308
from .headers import Headers


class Response:  # pylint: disable=too-few-public-methods
    """
    Response to a given `Request`. Use in `Server.route` handler functions.

    Base class for all other response classes.

    Example::

        @server.route(path, method)
        def route_func(request: Request):

            return Response(request, body='Some content', content_type="text/plain")
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        request: Request,
        body: Union[str, bytes] = "",
        *,
        status: Union[Status, Tuple[int, str]] = OK_200,
        headers: Union[Headers, Dict[str, str]] = None,
        content_type: str = None,
    ) -> None:
        """
        :param Request request: Request that this is a response to.
        :param str body: Body of response. Defaults to empty string.
        :param Status status: Status code and text. Defaults to 200 OK.
        :param Headers headers: Headers to include in response. Defaults to empty dict.
        :param str content_type: Content type of response. Defaults to None.
        """

        self._request = request
        self._body = body
        self._status = status if isinstance(status, Status) else Status(*status)
        self._headers = (
            headers.copy() if isinstance(headers, Headers) else Headers(headers)
        )
        self._content_type = content_type
        self._size = 0

    def _send_headers(
        self,
        content_length: Optional[int] = None,
        content_type: str = None,
    ) -> None:
        headers = self._headers.copy()

        response_message_header = (
            f"HTTP/1.1 {self._status.code} {self._status.text}\r\n"
        )

        headers.setdefault(
            "Content-Type", content_type or self._content_type or MIMETypes.DEFAULT
        )
        headers.setdefault("Connection", "close")
        if content_length is not None:
            headers.setdefault("Content-Length", content_length)

        for header, value in headers.items():
            response_message_header += f"{header}: {value}\r\n"
        response_message_header += "\r\n"

        self._send_bytes(
            self._request.connection, response_message_header.encode("utf-8")
        )

    def _send(self) -> None:
        encoded_body = (
            self._body.encode("utf-8") if isinstance(self._body, str) else self._body
        )

        self._send_headers(len(encoded_body), self._content_type)
        self._send_bytes(self._request.connection, encoded_body)

    def _send_bytes(
        self,
        conn: Union["SocketPool.Socket", "socket.socket"],
        buffer: Union[bytes, bytearray, memoryview],
    ):
        bytes_sent: int = 0
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
        self._size += bytes_sent


class FileResponse(Response):  # pylint: disable=too-few-public-methods
    """
    Specialized version of `Response` class for sending files.

    Instead of ``body`` it takes ``filename`` and ``root_path`` arguments.
    It is also possible to send only headers with ``head_only`` argument or modify ``buffer_size``.

    If browsers should download the file instead of displaying it, use ``as_attachment`` and
    ``download_filename`` arguments.

    Example::

        @server.route(path, method)
        def route_func(request: Request):

            return FileResponse(request, filename='index.html', root_path='/www')
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        request: Request,
        filename: str = "index.html",
        root_path: str = None,
        *,
        status: Union[Status, Tuple[int, str]] = OK_200,
        headers: Union[Headers, Dict[str, str]] = None,
        content_type: str = None,
        as_attachment: bool = False,
        download_filename: str = None,
        buffer_size: int = 1024,
        head_only: bool = False,
        safe: bool = True,
    ) -> None:
        """
        :param Request request: Request that this is a response to.
        :param str filename: Name of the file to send.
        :param str root_path: Path to the root directory from which to serve files. Defaults to
          server's ``root_path``.
        :param Status status: Status code and text. Defaults to 200 OK.
        :param Headers headers: Headers to include in response.
        :param str content_type: Content type of response.
        :param bool as_attachment: If True, the file will be sent as an attachment.
        :param str download_filename: Name of the file to send as an attachment.
        :param int buffer_size: Size of the buffer used to send the file. Defaults to 1024.
        :param bool head_only: If True, only headers will be sent. Defaults to False.
        :param bool safe: If True, checks if ``filename`` is valid. Defaults to True.
        """
        if safe:
            self._verify_file_path_is_valid(filename)

        super().__init__(
            request=request,
            headers=headers,
            content_type=content_type,
            status=status,
        )
        self._filename = filename + "index.html" if filename.endswith("/") else filename
        self._root_path = root_path or self._request.server.root_path
        self._full_file_path = self._combine_path(self._root_path, self._filename)
        self._content_type = content_type or MIMETypes.get_for_filename(self._filename)
        self._file_length = self._get_file_length(self._full_file_path)

        self._buffer_size = buffer_size
        self._head_only = head_only
        self._safe = safe

        if as_attachment:
            self._headers.setdefault(
                "Content-Disposition",
                f"attachment; filename={download_filename or self._filename.split('/')[-1]}",
            )

    @staticmethod
    def _verify_file_path_is_valid(file_path: str):
        """
        Verifies that ``file_path`` does not contain backslashes or parent directory references.

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
    def _combine_path(root_path: str, filename: str) -> str:
        """
        Combines ``root_path`` and ``filename`` into a single path.
        """

        if not root_path.endswith("/"):
            root_path += "/"
        if filename.startswith("/"):
            filename = filename[1:]

        return root_path + filename

    @staticmethod
    def _get_file_length(file_path: str) -> int:
        """
        Tries to get the length of the file at ``file_path``.
        Raises ``FileNotExistsError`` if file does not exist.
        """
        try:
            stat = os.stat(file_path)
            st_mode, st_size = stat[0], stat[6]
            assert (st_mode & 0o170000) == 0o100000  # Check if it is a regular file
            return st_size
        except (OSError, AssertionError):
            raise FileNotExistsError(file_path)  # pylint: disable=raise-missing-from

    def _send(self) -> None:
        self._send_headers(self._file_length, self._content_type)

        if not self._head_only:
            with open(self._full_file_path, "rb") as file:
                while bytes_read := file.read(self._buffer_size):
                    self._send_bytes(self._request.connection, bytes_read)


class ChunkedResponse(Response):  # pylint: disable=too-few-public-methods
    """
    Specialized version of `Response` class for sending data using chunked transfer encoding.

    Instead of requiring the whole content to be passed to the constructor, it expects
    a **generator** that yields chunks of data.

    Example::

        @server.route(path, method)
        def route_func(request: Request):

            def body():
                yield "Some ch"
                yield "unked co"
                yield "ntent"

            return ChunkedResponse(request, body, content_type="text/plain")
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        request: Request,
        body: Generator[Union[str, bytes], Any, Any],
        *,
        status: Union[Status, Tuple[int, str]] = OK_200,
        headers: Union[Headers, Dict[str, str]] = None,
        content_type: str = None,
    ) -> None:
        """
        :param Request request: Request object
        :param Generator body: Generator that yields chunks of data.
        :param Status status: Status object or tuple with code and message.
        :param Headers headers: Headers to be sent with the response.
        :param str content_type: Content type of the response.
        """

        super().__init__(
            request=request,
            headers=headers,
            status=status,
            content_type=content_type,
        )
        self._headers.setdefault("Transfer-Encoding", "chunked")
        self._body = body

    def _send_chunk(self, chunk: Union[str, bytes] = "") -> None:
        encoded_chunk = chunk.encode("utf-8") if isinstance(chunk, str) else chunk

        self._send_bytes(self._request.connection, b"%x\r\n" % len(encoded_chunk))
        self._send_bytes(self._request.connection, encoded_chunk)
        self._send_bytes(self._request.connection, b"\r\n")

    def _send(self) -> None:
        self._send_headers()

        for chunk in self._body():
            if 0 < len(chunk):  # Don't send empty chunks
                self._send_chunk(chunk)

        # Empty chunk to indicate end of response
        self._send_chunk()


class JSONResponse(Response):  # pylint: disable=too-few-public-methods
    """
    Specialized version of `Response` class for sending JSON data.

    Instead of requiring ``body`` to be passed to the constructor, it expects ``data`` to be passed
    instead.

    Example::

        @server.route(path, method)
        def route_func(request: Request):

            return JSONResponse(request, {"key": "value"})
    """

    def __init__(
        self,
        request: Request,
        data: Dict[Any, Any],
        *,
        headers: Union[Headers, Dict[str, str]] = None,
        status: Union[Status, Tuple[int, str]] = OK_200,
    ) -> None:
        """
        :param Request request: Request that this is a response to.
        :param dict data: Data to be sent as JSON.
        :param Headers headers: Headers to include in response.
        :param Status status: Status code and text. Defaults to 200 OK.
        """
        super().__init__(
            request=request,
            headers=headers,
            status=status,
        )
        self._data = data

    def _send(self) -> None:
        encoded_data = json.dumps(self._data).encode("utf-8")

        self._send_headers(len(encoded_data), "application/json")
        self._send_bytes(self._request.connection, encoded_data)


class Redirect(Response):  # pylint: disable=too-few-public-methods
    """
    Specialized version of `Response` class for redirecting to another URL.

    Instead of requiring the body to be passed to the constructor, it expects a URL to redirect to.

    Example::

        @server.route(path, method)
        def route_func(request: Request):

            return Redirect(request, "https://www.example.com")
    """

    def __init__(
        self,
        request: Request,
        url: str,
        *,
        permanent: bool = False,
        headers: Union[Headers, Dict[str, str]] = None,
    ) -> None:
        """
        :param Request request: Request that this is a response to.
        :param str url: URL to redirect to.
        :param bool permanent: Whether to use a permanent redirect (308) or a temporary one (307).
        :param Headers headers: Headers to include in response.
        """
        super().__init__(
            request,
            status=PERMANENT_REDIRECT_308 if permanent else TEMPORARY_REDIRECT_307,
            headers=headers,
        )
        self._headers.update({"Location": url})

    def _send(self) -> None:
        self._send_headers()
