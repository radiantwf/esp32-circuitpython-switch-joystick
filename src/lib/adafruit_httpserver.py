# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver`
================================================================================

Simple HTTP Server for CircuitPython


* Author(s): Dan Halbert

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
"""

try:
    from typing import Any, Callable, Optional
except ImportError:
    pass

from errno import EAGAIN, ECONNRESET
import os

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer.git"


class HTTPStatus:  # pylint: disable=too-few-public-methods
    """HTTP status codes."""

    def __init__(self, value, phrase):
        """Define a status code.

        :param int value: Numeric value: 200, 404, etc.
        :param str phrase: Short phrase: "OK", "Not Found', etc.
        """
        self.value = value
        self.phrase = phrase

    def __repr__(self):
        return f'HTTPStatus({self.value}, "{self.phrase}")'

    def __str__(self):
        return f"{self.value} {self.phrase}"


HTTPStatus.NOT_FOUND = HTTPStatus(404, "Not Found")
"""404 Not Found"""
HTTPStatus.OK = HTTPStatus(200, "OK")  # pylint: disable=invalid-name
"""200 OK"""
HTTPStatus.INTERNAL_SERVER_ERROR = HTTPStatus(500, "Internal Server Error")
"""500 Internal Server Error"""


class _HTTPRequest:
    def __init__(
        self, path: str = "", method: str = "", raw_request: bytes = None
    ) -> None:
        self.raw_request = raw_request
        if raw_request is None:
            self.path = path
            self.method = method
        else:
            # Parse request data from raw request
            request_text = raw_request.decode("utf8")
            first_line = request_text[: request_text.find("\n")]
            try:
                (self.method, self.path, _httpversion) = first_line.split()
            except ValueError as exc:
                raise ValueError("Unparseable raw_request: ", raw_request) from exc

    def __hash__(self) -> int:
        return hash(self.method) ^ hash(self.path)

    def __eq__(self, other: "_HTTPRequest") -> bool:
        return self.method == other.method and self.path == other.path

    def __repr__(self) -> str:
        return f"_HTTPRequest(path={repr(self.path)}, method={repr(self.method)})"


class MIMEType:
    """Common MIME types.
    From https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    """

    TEXT_PLAIN = "text/plain"

    _MIME_TYPES = {
        "aac": "audio/aac",
        "abw": "application/x-abiword",
        "arc": "application/x-freearc",
        "avi": "video/x-msvideo",
        "azw": "application/vnd.amazon.ebook",
        "bin": "application/octet-stream",
        "bmp": "image/bmp",
        "bz": "application/x-bzip",
        "bz2": "application/x-bzip2",
        "csh": "application/x-csh",
        "css": "text/css",
        "csv": "text/csv",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "eot": "application/vnd.ms-fontobject",
        "epub": "application/epub+zip",
        "gz": "application/gzip",
        "gif": "image/gif",
        "html": "text/html",
        "htm": "text/html",
        "ico": "image/vnd.microsoft.icon",
        "ics": "text/calendar",
        "jar": "application/java-archive",
        "jpeg .jpg": "image/jpeg",
        "js": "text/javascript",
        "json": "application/json",
        "jsonld": "application/ld+json",
        "mid": "audio/midi",
        "midi": "audio/midi",
        "mjs": "text/javascript",
        "mp3": "audio/mpeg",
        "cda": "application/x-cdf",
        "mp4": "video/mp4",
        "mpeg": "video/mpeg",
        "mpkg": "application/vnd.apple.installer+xml",
        "odp": "application/vnd.oasis.opendocument.presentation",
        "ods": "application/vnd.oasis.opendocument.spreadsheet",
        "odt": "application/vnd.oasis.opendocument.text",
        "oga": "audio/ogg",
        "ogv": "video/ogg",
        "ogx": "application/ogg",
        "opus": "audio/opus",
        "otf": "font/otf",
        "png": "image/png",
        "pdf": "application/pdf",
        "php": "application/x-httpd-php",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "rar": "application/vnd.rar",
        "rtf": "application/rtf",
        "sh": "application/x-sh",
        "svg": "image/svg+xml",
        "swf": "application/x-shockwave-flash",
        "tar": "application/x-tar",
        "tiff": "image/tiff",
        "tif": "image/tiff",
        "ts": "video/mp2t",
        "ttf": "font/ttf",
        "txt": TEXT_PLAIN,
        "vsd": "application/vnd.visio",
        "wav": "audio/wav",
        "weba": "audio/webm",
        "webm": "video/webm",
        "webp": "image/webp",
        "woff": "font/woff",
        "woff2": "font/woff2",
        "xhtml": "application/xhtml+xml",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xml": "application/xml",
        "xul": "application/vnd.mozilla.xul+xml",
        "zip": "application/zip",
        "7z": "application/x-7z-compressed",
    }

    @staticmethod
    def mime_type(filename):
        """Return the mime type for the given filename. If not known, return "text/plain"."""
        return MIMEType._MIME_TYPES.get(filename.split(".")[-1], MIMEType.TEXT_PLAIN)


class HTTPResponse:
    """Details of an HTTP response. Use in `HTTPServer.route` decorator functions."""

    _HEADERS_FORMAT = (
        "HTTP/1.1 {}\r\n"
        "Content-Type: {}\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    def __init__(
        self,
        *,
        status: tuple = HTTPStatus.OK,
        content_type: str = MIMEType.TEXT_PLAIN,
        body: str = "",
        filename: Optional[str] = None,
        root: str = "",
    ) -> None:
        """Create an HTTP response.

        :param tuple status: The HTTP status code to return, as a tuple of (int, "message").
          Common statuses are available in `HTTPStatus`.
        :param str content_type: The MIME type of the data being returned.
          Common MIME types are available in `MIMEType`.
        :param Union[str|bytes] body:
          The data to return in the response body, if ``filename`` is not ``None``.
        :param str filename: If not ``None``,
          return the contents of the specified file, and ignore ``body``.
        :param str root: root directory for filename, without a trailing slash
        """
        self.status = status
        self.content_type = content_type
        self.body = body.encode() if isinstance(body, str) else body
        self.filename = filename

        self.root = root

    def send(self, conn: Any) -> None:
        # TODO: Use Union[SocketPool.Socket | socket.socket] for the type annotation in some way.
        """Send the constructed response over the given socket."""
        if self.filename:
            try:
                file_length = os.stat(self.root + self.filename)[6]
                self._send_file_response(conn, self.filename, self.root, file_length)
            except OSError:
                self._send_response(
                    conn,
                    HTTPStatus.NOT_FOUND,
                    MIMEType.TEXT_PLAIN,
                    f"{HTTPStatus.NOT_FOUND} {self.filename}\r\n",
                )
        else:
            self._send_response(conn, self.status, self.content_type, self.body)

    def _send_response(self, conn, status, content_type, body):
        self._send_bytes(
            conn, self._HEADERS_FORMAT.format(status, content_type, len(body))
        )
        self._send_bytes(conn, body)

    def _send_file_response(self, conn, filename, root, file_length):
        self._send_bytes(
            conn,
            self._HEADERS_FORMAT.format(
                self.status, MIMEType.mime_type(filename), file_length
            ),
        )
        with open(root + filename, "rb") as file:
            while bytes_read := file.read(8192):
                self._send_bytes(conn, bytes_read)

    def _send_bytes(self, conn, buf):  # pylint: disable=no-self-use
        bytes_sent = 0
        bytes_to_send = len(buf)
        view = memoryview(buf)
        while bytes_sent < bytes_to_send:
            try:
                bytes_sent += conn.send(view[bytes_sent:])
            except OSError as exc:
                if exc.errno == EAGAIN:
                    continue
                if exc.errno == ECONNRESET:
                    return


class HTTPServer:
    """A basic socket-based HTTP server."""

    def __init__(self, socket_source: Any) -> None:
        # TODO: Use a Protocol for the type annotation.
        # The Protocol could be refactored from adafruit_requests.
        """Create a server, and get it ready to run.

        :param socket: An object that is a source of sockets. This could be a `socketpool`
          in CircuitPython or the `socket` module in CPython.
        """
        self._buffer = bytearray(1024)
        self.routes = {}
        self._socket_source = socket_source
        self._sock = None
        self.root_path = "/"

    def route(self, path: str, method: str = "GET"):
        """Decorator used to add a route.

        :param str path: filename path
        :param str method: HTTP method: "GET", "POST", etc.

        Example::

            @server.route(path, method)
            def route_func(request):
                raw_text = request.raw_request.decode("utf8")
                print("Received a request of length", len(raw_text), "bytes")
                return HTTPResponse(body="hello world")

        """

        def route_decorator(func: Callable) -> Callable:
            self.routes[_HTTPRequest(path, method)] = func
            return func

        return route_decorator

    def serve_forever(self, host: str, port: int = 80, root: str = "") -> None:
        """Wait for HTTP requests at the given host and port. Does not return.

        :param str host: host name or IP address
        :param int port: port
        :param str root: root directory to serve files from
        """
        self.start(host, port, root)

        while True:
            try:
                self.poll()
            except OSError:
                continue

    def start(self, host: str, port: int = 80, root: str = "") -> None:
        """
        Start the HTTP server at the given host and port. Requires calling
        poll() in a while loop to handle incoming requests.

        :param str host: host name or IP address
        :param int port: port
        :param str root: root directory to serve files from
        """
        self.root_path = root

        self._sock = self._socket_source.socket(
            self._socket_source.AF_INET, self._socket_source.SOCK_STREAM
        )
        self._sock.bind((host, port))
        self._sock.listen(10)
        self._sock.setblocking(False)  # non-blocking socket

    def poll(self):
        """
        Call this method inside your main event loop to get the server to
        check for new incoming client requests. When a request comes in,
        the application callable will be invoked.
        """
        try:
            conn, _ = self._sock.accept()
            with conn:
                length, _ = conn.recvfrom_into(self._buffer)

                request = _HTTPRequest(raw_request=self._buffer[:length])

                # If a route exists for this request, call it. Otherwise try to serve a file.
                route = self.routes.get(request, None)
                if route:
                    response = route(request)
                elif request.method == "GET":
                    response = HTTPResponse(filename=request.path, root=self.root_path)
                else:
                    response = HTTPResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

                response.send(conn)
        except OSError as ex:
            # handle EAGAIN and ECONNRESET
            if ex.errno == EAGAIN:
                # there is no data available right now, try again later.
                return
            if ex.errno == ECONNRESET:
                # connection reset by peer, try again later.
                return
            raise

    @property
    def request_buffer_size(self) -> int:
        """
        The maximum size of the incoming request buffer. If the default size isn't
        adequate to handle your incoming data you can set this after creating the
        server instance.

        Default size is 1024 bytes.

        Example::

            server = HTTPServer(pool)
            server.request_buffer_size = 2048

            server.serve_forever(str(wifi.radio.ipv4_address))
        """
        return len(self._buffer)

    @request_buffer_size.setter
    def request_buffer_size(self, value: int) -> None:
        self._buffer = bytearray(value)