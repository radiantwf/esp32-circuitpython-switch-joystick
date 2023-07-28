# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.request`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""

try:
    from typing import List, Dict, Tuple, Union, Any, TYPE_CHECKING
    from socket import socket
    from socketpool import SocketPool

    if TYPE_CHECKING:
        from .server import Server
except ImportError:
    pass

import json

from .headers import Headers


class _IFieldStorage:
    """Interface with shared methods for QueryParams and FormData."""

    _storage: Dict[str, List[Union[str, bytes]]]

    def _add_field_value(self, field_name: str, value: Union[str, bytes]) -> None:
        if field_name not in self._storage:
            self._storage[field_name] = [value]
        else:
            self._storage[field_name].append(value)

    def get(self, field_name: str, default: Any = None) -> Union[str, bytes, None]:
        """Get the value of a field."""
        return self._storage.get(field_name, [default])[0]

    def get_list(self, field_name: str) -> List[Union[str, bytes]]:
        """Get the list of values of a field."""
        return self._storage.get(field_name, [])

    @property
    def fields(self):
        """Returns a list of field names."""
        return list(self._storage.keys())

    def __getitem__(self, field_name: str):
        return self.get(field_name)

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

    def __contains__(self, key: str):
        return key in self._storage

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._storage)})"


class QueryParams(_IFieldStorage):
    """
    Class for parsing and storing GET quer parameters requests.

    Examples::

        query_params = QueryParams(b"foo=bar&baz=qux&baz=quux")
        # QueryParams({"foo": "bar", "baz": ["qux", "quux"]})

        query_params.get("foo") # "bar"
        query_params["foo"] # "bar"
        query_params.get("non-existent-key") # None
        query_params.get_list("baz") # ["qux", "quux"]
        "unknown-key" in query_params # False
        query_params.fields # ["foo", "baz"]
    """

    _storage: Dict[str, List[Union[str, bytes]]]

    def __init__(self, query_string: str) -> None:
        self._storage = {}

        for query_param in query_string.split("&"):
            if "=" in query_param:
                key, value = query_param.split("=", 1)
                self._add_field_value(key, value)
            elif query_param:
                self._add_field_value(query_param, "")


class FormData(_IFieldStorage):
    """
    Class for parsing and storing form data from POST requests.

    Supports ``application/x-www-form-urlencoded``, ``multipart/form-data`` and ``text/plain``
    content types.

    Examples::

        form_data = FormData(b"foo=bar&baz=qux&baz=quuz", "application/x-www-form-urlencoded")
        # or
        form_data = FormData(b"foo=bar\\r\\nbaz=qux\\r\\nbaz=quux", "text/plain")
        # FormData({"foo": "bar", "baz": "qux"})

        form_data.get("foo") # "bar"
        form_data["foo"] # "bar"
        form_data.get("non-existent-key") # None
        form_data.get_list("baz") # ["qux", "quux"]
        "unknown-key" in form_data # False
        form_data.fields # ["foo", "baz"]
    """

    _storage: Dict[str, List[Union[str, bytes]]]

    def __init__(self, data: bytes, content_type: str) -> None:
        self.content_type = content_type
        self._storage = {}

        if content_type.startswith("application/x-www-form-urlencoded"):
            self._parse_x_www_form_urlencoded(data)

        elif content_type.startswith("multipart/form-data"):
            boundary = content_type.split("boundary=")[1]
            self._parse_multipart_form_data(data, boundary)

        elif content_type.startswith("text/plain"):
            self._parse_text_plain(data)

    def _parse_x_www_form_urlencoded(self, data: bytes) -> None:
        decoded_data = data.decode()

        for field_name, value in [
            key_value.split("=", 1) for key_value in decoded_data.split("&")
        ]:
            self._add_field_value(field_name, value)

    def _parse_multipart_form_data(self, data: bytes, boundary: str) -> None:
        blocks = data.split(b"--" + boundary.encode())[1:-1]

        for block in blocks:
            disposition, content = block.split(b"\r\n\r\n", 1)
            field_name = disposition.split(b'"', 2)[1].decode()
            value = content[:-2]

            self._add_field_value(field_name, value)

    def _parse_text_plain(self, data: bytes) -> None:
        lines = data.split(b"\r\n")[:-1]

        for line in lines:
            field_name, value = line.split(b"=", 1)

            self._add_field_value(field_name.decode(), value.decode())


class Request:
    """
    Incoming request, constructed from raw incoming bytes.
    It is passed as first argument to all route handlers.
    """

    server: "Server"
    """
    Server object that received the request.
    """

    connection: Union["SocketPool.Socket", "socket.socket"]
    """
    Socket object used to send and receive data on the connection.
    """

    client_address: Tuple[str, int]
    """
    Address and port bound to the socket on the other end of the connection.

    Example::

        request.client_address  # ('192.168.137.1', 40684)
    """

    method: str
    """Request method e.g. "GET" or "POST"."""

    path: str
    """Path of the request, e.g. ``"/foo/bar"``."""

    query_params: QueryParams
    """
    Query/GET parameters in the request.

    Example::

        request  = Request(..., raw_request=b"GET /?foo=bar&baz=qux HTTP/1.1...")

        request.query_params                  # QueryParams({"foo": "bar"})
        request.query_params["foo"]           # "bar"
        request.query_params.get_list("baz")  # ["qux"]
    """

    http_version: str
    """HTTP version, e.g. ``"HTTP/1.1"``."""

    headers: Headers
    """
    Headers from the request.
    """

    raw_request: bytes
    """
    Raw 'bytes' that were received from the client.

    Should **not** be modified directly.
    """

    def __init__(
        self,
        server: "Server",
        connection: Union["SocketPool.Socket", "socket.socket"],
        client_address: Tuple[str, int],
        raw_request: bytes = None,
    ) -> None:
        self.server = server
        self.connection = connection
        self.client_address = client_address
        self.raw_request = raw_request
        self._form_data = None

        if raw_request is None:
            raise ValueError("raw_request cannot be None")

        header_bytes = self._raw_header_bytes

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
        return self._raw_body_bytes

    @body.setter
    def body(self, body: bytes) -> None:
        self.raw_request = self._raw_header_bytes + b"\r\n\r\n" + body

    @property
    def form_data(self) -> Union[FormData, None]:
        """
        POST data of the request.

        Example::

            # application/x-www-form-urlencoded
            request = Request(...,
                raw_request=b\"\"\"...
                foo=bar&baz=qux\"\"\"
            )

            # or

            # multipart/form-data
            request = Request(...,
                raw_request=b\"\"\"...
                --boundary
                Content-Disposition: form-data; name="foo"

                bar
                --boundary
                Content-Disposition: form-data; name="baz"

                qux
                --boundary--\"\"\"
            )

            # or

            # text/plain
            request = Request(...,
                raw_request=b\"\"\"...
                foo=bar
                baz=qux
                \"\"\"
            )

            request.form_data                  # FormData({'foo': ['bar'], 'baz': ['qux']})
            request.form_data["foo"]           # "bar"
            request.form_data.get_list("baz")  # ["qux"]
        """
        if self._form_data is None and self.method == "POST":
            self._form_data = FormData(self.body, self.headers["Content-Type"])
        return self._form_data

    def json(self) -> Union[dict, None]:
        """Body of the request, as a JSON-decoded dictionary."""
        return json.loads(self.body) if self.body else None

    @property
    def _raw_header_bytes(self) -> bytes:
        """Returns headers bytes."""
        empty_line_index = self.raw_request.find(b"\r\n\r\n")

        return self.raw_request[:empty_line_index]

    @property
    def _raw_body_bytes(self) -> bytes:
        """Returns body bytes."""
        empty_line_index = self.raw_request.find(b"\r\n\r\n")

        return self.raw_request[empty_line_index + 4 :]

    @staticmethod
    def _parse_start_line(header_bytes: bytes) -> Tuple[str, str, Dict[str, str], str]:
        """Parse HTTP Start line to method, path, query_params and http_version."""

        start_line = header_bytes.decode("utf8").splitlines()[0]

        method, path, http_version = start_line.split()

        if "?" not in path:
            path += "?"

        path, query_string = path.split("?", 1)

        query_params = QueryParams(query_string)

        return method, path, query_params, http_version

    @staticmethod
    def _parse_headers(header_bytes: bytes) -> Headers:
        """Parse HTTP headers from raw request."""
        header_lines = header_bytes.decode("utf8").splitlines()[1:]

        return Headers(
            {
                name: value
                for header_line in header_lines
                for name, value in [header_line.split(": ", 1)]
            }
        )
