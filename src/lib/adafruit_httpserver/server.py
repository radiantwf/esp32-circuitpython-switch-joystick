# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.server.HTTPServer`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""

try:
    from typing import Callable, Protocol, Union
    from socket import socket
    from socketpool import SocketPool
except ImportError:
    pass

from errno import EAGAIN, ECONNRESET, ETIMEDOUT

from .exceptions import FileNotExistsError, InvalidPathError
from .methods import HTTPMethod
from .request import HTTPRequest
from .response import HTTPResponse
from .route import _HTTPRoutes, _HTTPRoute
from .status import CommonHTTPStatus


class HTTPServer:
    """A basic socket-based HTTP server."""

    def __init__(self, socket_source: Protocol, root_path: str) -> None:
        """Create a server, and get it ready to run.

        :param socket: An object that is a source of sockets. This could be a `socketpool`
          in CircuitPython or the `socket` module in CPython.
        :param str root_path: Root directory to serve files from
        """
        self._buffer = bytearray(1024)
        self._timeout = 1
        self.routes = _HTTPRoutes()
        self._socket_source = socket_source
        self._sock = None
        self.root_path = root_path

    def route(self, path: str, method: HTTPMethod = HTTPMethod.GET) -> Callable:
        """
        Decorator used to add a route.

        :param str path: URL path
        :param HTTPMethod method: HTTP method: HTTPMethod.GET, HTTPMethod.POST, etc.

        Example::

            @server.route("/example", HTTPMethod.GET)
            def route_func(request):
                ...

            @server.route("/example/<my_parameter>", HTTPMethod.GET)
            def route_func(request, my_parameter):
                ...
        """

        def route_decorator(func: Callable) -> Callable:
            self.routes.add(_HTTPRoute(path, method), func)
            return func

        return route_decorator

    def serve_forever(self, host: str, port: int = 80) -> None:
        """Wait for HTTP requests at the given host and port. Does not return.

        :param str host: host name or IP address
        :param int port: port
        """
        self.start(host, port)

        while True:
            try:
                self.poll()
            except OSError:
                continue

    def start(self, host: str, port: int = 80) -> None:
        """
        Start the HTTP server at the given host and port. Requires calling
        poll() in a while loop to handle incoming requests.

        :param str host: host name or IP address
        :param int port: port
        """
        self._sock = self._socket_source.socket(
            self._socket_source.AF_INET, self._socket_source.SOCK_STREAM
        )
        self._sock.bind((host, port))
        self._sock.listen(10)
        self._sock.setblocking(False)  # non-blocking socket

    def _receive_header_bytes(
        self, sock: Union["SocketPool.Socket", "socket.socket"]
    ) -> bytes:
        """Receive bytes until a empty line is received."""
        received_bytes = bytes()
        while b"\r\n\r\n" not in received_bytes:
            try:
                length = sock.recv_into(self._buffer, len(self._buffer))
                received_bytes += self._buffer[:length]
            except OSError as ex:
                if ex.errno == ETIMEDOUT:
                    break
                raise
            except Exception as ex:
                raise ex
        return received_bytes

    def _receive_body_bytes(
        self,
        sock: Union["SocketPool.Socket", "socket.socket"],
        received_body_bytes: bytes,
        content_length: int,
    ) -> bytes:
        """Receive bytes until the given content length is received."""
        while len(received_body_bytes) < content_length:
            try:
                length = sock.recv_into(self._buffer, len(self._buffer))
                received_body_bytes += self._buffer[:length]
            except OSError as ex:
                if ex.errno == ETIMEDOUT:
                    break
                raise
            except Exception as ex:
                raise ex
        return received_body_bytes[:content_length]

    def poll(self):
        """
        Call this method inside your main event loop to get the server to
        check for new incoming client requests. When a request comes in,
        the application callable will be invoked.
        """
        try:
            conn, client_address = self._sock.accept()
            with conn:
                conn.settimeout(self._timeout)

                # Receiving data until empty line
                header_bytes = self._receive_header_bytes(conn)

                # Return if no data received
                if not header_bytes:
                    return

                request = HTTPRequest(conn, client_address, header_bytes)

                content_length = int(request.headers.get("Content-Length", 0))
                received_body_bytes = request.body

                # Receiving remaining body bytes
                request.body = self._receive_body_bytes(
                    conn, received_body_bytes, content_length
                )

                # Find a handler for the route
                handler = self.routes.find_handler(
                    _HTTPRoute(request.path, request.method)
                )

                try:
                    # If a handler for route exists and is callable, call it.
                    if handler is not None and callable(handler):
                        handler(request)

                    # If no handler exists and request method is GET or HEAD, try to serve a file.
                    elif handler is None and request.method in (
                        HTTPMethod.GET,
                        HTTPMethod.HEAD,
                    ):
                        filename = "index.html" if request.path == "/" else request.path
                        HTTPResponse(request).send_file(
                            filename=filename,
                            root_path=self.root_path,
                            buffer_size=self.request_buffer_size,
                            head_only=(request.method == HTTPMethod.HEAD),
                        )
                    else:
                        HTTPResponse(
                            request, status=CommonHTTPStatus.BAD_REQUEST_400
                        ).send()

                except InvalidPathError as error:
                    HTTPResponse(request, status=CommonHTTPStatus.FORBIDDEN_403).send(
                        str(error)
                    )

                except FileNotExistsError as error:
                    HTTPResponse(request, status=CommonHTTPStatus.NOT_FOUND_404).send(
                        str(error)
                    )

        except OSError as error:
            # Handle EAGAIN and ECONNRESET
            if error.errno == EAGAIN:
                # There is no data available right now, try again later.
                return
            if error.errno == ECONNRESET:
                # Connection reset by peer, try again later.
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

            server = HTTPServer(pool, "/static")
            server.request_buffer_size = 2048

            server.serve_forever(str(wifi.radio.ipv4_address))
        """
        return len(self._buffer)

    @request_buffer_size.setter
    def request_buffer_size(self, value: int) -> None:
        self._buffer = bytearray(value)

    @property
    def socket_timeout(self) -> int:
        """
        Timeout after which the socket will stop waiting for more incoming data.

        Must be set to positive integer or float. Default is 1 second.

        When exceeded, raises `OSError` with `errno.ETIMEDOUT`.

        Example::

            server = HTTPServer(pool, "/static")
            server.socket_timeout = 3

            server.serve_forever(str(wifi.radio.ipv4_address))
        """
        return self._timeout

    @socket_timeout.setter
    def socket_timeout(self, value: int) -> None:
        if isinstance(value, (int, float)) and value > 0:
            self._timeout = value
        else:
            raise ValueError(
                "HTTPServer.socket_timeout must be a positive numeric value."
            )
