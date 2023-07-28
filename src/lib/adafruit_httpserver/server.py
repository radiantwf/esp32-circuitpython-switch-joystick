# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.server`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""

try:
    from typing import Callable, Protocol, Union, List, Set, Tuple, Dict
    from socket import socket
    from socketpool import SocketPool
except ImportError:
    pass

from errno import EAGAIN, ECONNRESET, ETIMEDOUT
from traceback import print_exception

from .authentication import Basic, Bearer, require_authentication
from .exceptions import (
    ServerStoppedError,
    AuthenticationError,
    FileNotExistsError,
    InvalidPathError,
    ServingFilesDisabledError,
)
from .headers import Headers
from .methods import GET, HEAD
from .request import Request
from .response import Response, FileResponse
from .route import _Routes, _Route
from .status import BAD_REQUEST_400, UNAUTHORIZED_401, FORBIDDEN_403, NOT_FOUND_404


NO_REQUEST = "no_request"
CONNECTION_TIMED_OUT = "connection_timed_out"
REQUEST_HANDLED_NO_RESPONSE = "request_handled_no_response"
REQUEST_HANDLED_RESPONSE_SENT = "request_handled_response_sent"


class Server:  # pylint: disable=too-many-instance-attributes
    """A basic socket-based HTTP server."""

    host: str
    """Host name or IP address the server is listening on. ``None`` if server is stopped."""

    port: int
    """Port the server is listening on. ``None`` if server is stopped."""

    root_path: str
    """Root directory to serve files from. ``None`` if serving files is disabled."""

    def __init__(
        self, socket_source: Protocol, root_path: str = None, *, debug: bool = False
    ) -> None:
        """Create a server, and get it ready to run.

        :param socket: An object that is a source of sockets. This could be a `socketpool`
          in CircuitPython or the `socket` module in CPython.
        :param str root_path: Root directory to serve files from
        :param bool debug: Enables debug messages useful during development
        """
        self._auths = []
        self._buffer = bytearray(1024)
        self._timeout = 1
        self._routes = _Routes()
        self._socket_source = socket_source
        self._sock = None
        self.headers = Headers()
        self.host, self.port = None, None
        self.root_path = root_path
        if root_path in ["", "/"] and debug:
            _debug_warning_exposed_files(root_path)
        self.stopped = True

        self.debug = debug

    def route(
        self,
        path: str,
        methods: Union[str, Set[str]] = GET,
        *,
        append_slash: bool = False,
    ) -> Callable:
        """
        Decorator used to add a route.

        If request matches multiple routes, the first matched one added will be used.

        :param str path: URL path
        :param str methods: HTTP method(s): ``"GET"``, ``"POST"``, ``["GET", "POST"]`` etc.
        :param bool append_slash: If True, the route will be accessible with and without a
          trailing slash

        Example::

            # Default method is GET
            @server.route("/example")
            def route_func(request):
                ...

            # It is necessary to specify other methods like POST, PUT, etc.
            @server.route("/example", POST)
            def route_func(request):
                ...

            # If you want to access URL with and without trailing slash, use append_slash=True
            @server.route("/example-with-slash", append_slash=True)
            # which is equivalent to
            @server.route("/example-with-slash")
            @server.route("/example-with-slash/")
            def route_func(request):
                ...

            # Multiple methods can be specified
            @server.route("/example", [GET, POST])
            def route_func(request):
                ...

            # URL parameters can be specified
            @server.route("/example/<my_parameter>", GET) e.g. /example/123
            def route_func(request, my_parameter):
                ...

            # It is possible to use wildcard that can match any number of path segments
            @server.route("/example/.../something", GET) # e.g. /example/123/something
            @server.route("/example/..../something", GET) # e.g. /example/123/456/something
            def route_func(request):
                ...
        """
        if path.endswith("/") and append_slash:
            raise ValueError("Cannot use append_slash=True when path ends with /")

        methods = set(methods) if isinstance(methods, (set, list)) else set([methods])

        def route_decorator(func: Callable) -> Callable:
            self._routes.add(_Route(path, methods, append_slash), func)
            return func

        return route_decorator

    def _verify_can_start(self, host: str, port: int) -> None:
        """Check if the server can be successfully started. Raises RuntimeError if not."""

        if host is None or port is None:
            raise RuntimeError("Host and port cannot be None")

        try:
            self._socket_source.getaddrinfo(host, port)
        except OSError as error:
            raise RuntimeError(f"Cannot start server on {host}:{port}") from error

    def serve_forever(self, host: str, port: int = 80) -> None:
        """
        Wait for HTTP requests at the given host and port. Does not return.
        Ignores any exceptions raised by the handler function and continues to serve.
        Returns only when the server is stopped by calling ``.stop()``.

        :param str host: host name or IP address
        :param int port: port
        """
        self.start(host, port)

        while not self.stopped:
            try:
                self.poll()
            except KeyboardInterrupt:  # Exit on Ctrl-C e.g. during development
                self.stop()
                return
            except Exception:  # pylint: disable=broad-except
                pass  # Ignore exceptions in handler function

    def start(self, host: str, port: int = 80) -> None:
        """
        Start the HTTP server at the given host and port. Requires calling
        ``.poll()`` in a while loop to handle incoming requests.

        :param str host: host name or IP address
        :param int port: port
        """
        self._verify_can_start(host, port)

        self.host, self.port = host, port

        self.stopped = False
        self._sock = self._socket_source.socket(
            self._socket_source.AF_INET, self._socket_source.SOCK_STREAM
        )
        self._sock.bind((host, port))
        self._sock.listen(10)
        self._sock.setblocking(False)  # Non-blocking socket

        if self.debug:
            _debug_started_server(self)

    def stop(self) -> None:
        """
        Stops the server from listening for new connections and closes the socket.
        Current requests will be processed. Server can be started again by calling ``.start()``
        or ``.serve_forever()``.
        """
        self.host, self.port = None, None

        self.stopped = True
        self._sock.close()

        if self.debug:
            _debug_stopped_server(self)

    def _receive_request(
        self,
        sock: Union["SocketPool.Socket", "socket.socket"],
        client_address: Tuple[str, int],
    ) -> Request:
        """Receive bytes from socket until the whole request is received."""

        # Receiving data until empty line
        header_bytes = self._receive_header_bytes(sock)

        # Return if no data received
        if not header_bytes:
            return None

        request = Request(self, sock, client_address, header_bytes)

        content_length = int(request.headers.get("Content-Length", 0))
        received_body_bytes = request.body

        # Receiving remaining body bytes
        request.body = self._receive_body_bytes(
            sock, received_body_bytes, content_length
        )

        return request

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

    def _handle_request(
        self, request: Request, handler: Union[Callable, None]
    ) -> Union[Response, None]:
        try:
            # Check server authentications if necessary
            if self._auths:
                require_authentication(request, self._auths)

            # Handler for route exists and is callable
            if handler is not None and callable(handler):
                return handler(request)

            # No root_path, access to filesystem disabled, return 404.
            if self.root_path is None:
                raise ServingFilesDisabledError

            # Method is GET or HEAD, try to serve a file from the filesystem.
            if request.method in [GET, HEAD]:
                return FileResponse(
                    request,
                    filename=request.path,
                    root_path=self.root_path,
                    head_only=request.method == HEAD,
                )

            return Response(request, status=BAD_REQUEST_400)

        except AuthenticationError:
            return Response(
                request,
                status=UNAUTHORIZED_401,
                headers={"WWW-Authenticate": 'Basic charset="UTF-8"'},
            )

        except InvalidPathError as error:
            return Response(
                request,
                str(error) if self.debug else "Invalid path",
                status=FORBIDDEN_403,
            )

        except (FileNotExistsError, ServingFilesDisabledError) as error:
            return Response(
                request,
                str(error) if self.debug else "File not found",
                status=NOT_FOUND_404,
            )

    def _set_default_server_headers(self, response: Response) -> None:
        for name, value in self.headers.items():
            response._headers.setdefault(  # pylint: disable=protected-access
                name, value
            )

    def poll(self) -> str:
        """
        Call this method inside your main loop to get the server to check for new incoming client
        requests. When a request comes in, it will be handled by the handler function.

        Returns str representing the result of the poll
        e.g. ``NO_REQUEST`` or ``REQUEST_HANDLED_RESPONSE_SENT``.
        """
        if self.stopped:
            raise ServerStoppedError

        try:
            conn, client_address = self._sock.accept()
            with conn:
                conn.settimeout(self._timeout)

                # Receive the whole request
                if (request := self._receive_request(conn, client_address)) is None:
                    return CONNECTION_TIMED_OUT

                # Find a handler for the route
                handler = self._routes.find_handler(
                    _Route(request.path, request.method)
                )

                # Handle the request
                response = self._handle_request(request, handler)

                if response is None:
                    return REQUEST_HANDLED_NO_RESPONSE

                self._set_default_server_headers(response)

                # Send the response
                response._send()  # pylint: disable=protected-access

                if self.debug:
                    _debug_response_sent(response)

                return REQUEST_HANDLED_RESPONSE_SENT

        except Exception as error:  # pylint: disable=broad-except
            if isinstance(error, OSError):
                # There is no data available right now, try again later.
                if error.errno == EAGAIN:
                    return NO_REQUEST
                # Connection reset by peer, try again later.
                if error.errno == ECONNRESET:
                    return NO_REQUEST

            if self.debug:
                _debug_exception_in_handler(error)

            raise error  # Raise the exception again to be handled by the user.

    def require_authentication(self, auths: List[Union[Basic, Bearer]]) -> None:
        """
        Requires authentication for all routes and files in ``root_path``.
        Any non-authenticated request will be rejected with a 401 status code.

        Example::

            server = Server(pool, "/static")
            server.require_authentication([Basic("username", "password")])
        """
        self._auths = auths

    @property
    def headers(self) -> Headers:
        """
        Headers to be sent with every response, without the need to specify them in each handler.

        If a header is specified in both the handler and the server, the handler's header will be
        used.

        Example::

            server = Server(pool, "/static")
            server.headers = {
                "X-Server": "Adafruit CircuitPython HTTP Server",
                "Access-Control-Allow-Origin": "*",
            }
        """
        return self._headers

    @headers.setter
    def headers(self, value: Union[Headers, Dict[str, str]]) -> None:
        self._headers = value.copy() if isinstance(value, Headers) else Headers(value)

    @property
    def request_buffer_size(self) -> int:
        """
        The maximum size of the incoming request buffer. If the default size isn't
        adequate to handle your incoming data you can set this after creating the
        server instance.

        Default size is 1024 bytes.

        Example::

            server = Server(pool, "/static")
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

            server = Server(pool, "/static")
            server.socket_timeout = 3

            server.serve_forever(str(wifi.radio.ipv4_address))
        """
        return self._timeout

    @socket_timeout.setter
    def socket_timeout(self, value: int) -> None:
        if isinstance(value, (int, float)) and value > 0:
            self._timeout = value
        else:
            raise ValueError("Server.socket_timeout must be a positive numeric value.")


def _debug_warning_exposed_files(root_path: str):
    """Warns about exposing all files on the device."""
    print(
        f"WARNING: Setting root_path to '{root_path}' will expose all files on your device through"
        " the webserver, including potentially sensitive files like settings.toml or secrets.py. "
        "Consider making a sub-directory on your device and using that for your root_path instead."
    )


def _debug_started_server(server: "Server"):
    """Prints a message when the server starts."""
    host, port = server.host, server.port

    print(f"Started development server on http://{host}:{port}")


def _debug_response_sent(response: "Response"):
    """Prints a message when after a response is sent."""
    # pylint: disable=protected-access
    client_ip = response._request.client_address[0]
    method = response._request.method
    path = response._request.path
    req_size = len(response._request.raw_request)
    status = response._status
    res_size = response._size

    print(f'{client_ip} -- "{method} {path}" {req_size} -- "{status}" {res_size}')


def _debug_stopped_server(server: "Server"):  # pylint: disable=unused-argument
    """Prints a message after the server stops."""
    print("Stopped development server")


def _debug_exception_in_handler(error: Exception):
    """Prints a message when an exception is raised in a handler."""
    print_exception(error)
