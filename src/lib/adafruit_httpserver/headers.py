# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.headers`
====================================================
* Author(s): Michał Pokusa
"""

try:
    from typing import Dict, Tuple
except ImportError:
    pass


class Headers:
    """
    A dict-like class for storing HTTP headers.

    Allows access to headers using **case insensitive** names.

    Does **not** implement all dict methods.

    Examples::

        headers = Headers({"Content-Type": "text/html", "Content-Length": "1024"})

        len(headers)
        # 2

        headers.setdefault("Access-Control-Allow-Origin", "*")
        headers["Access-Control-Allow-Origin"]
        # '*'

        headers["Content-Length"]
        # '1024'

        headers["content-type"]
        # 'text/html'

        headers["User-Agent"]
        # KeyError: User-Agent

        "CONTENT-TYPE" in headers
        # True
    """

    _storage: Dict[str, Tuple[str, str]]

    def __init__(self, headers: Dict[str, str] = None) -> None:
        headers = headers or {}

        self._storage = {key.lower(): [key, value] for key, value in headers.items()}

    def get(self, name: str, default: str = None):
        """Returns the value for the given header name, or default if not found."""
        return self._storage.get(name.lower(), [None, default])[1]

    def setdefault(self, name: str, default: str = None):
        """Sets the value for the given header name if it does not exist."""
        return self._storage.setdefault(name.lower(), [name, default])[1]

    def items(self):
        """Returns a list of (name, value) tuples."""
        return dict(self._storage.values()).items()

    def keys(self):
        """Returns a list of header names."""
        return dict(self._storage.values()).keys()

    def values(self):
        """Returns a list of header values."""
        return dict(self._storage.values()).values()

    def update(self, headers: Dict[str, str]):
        """Updates the headers with the given dict."""
        return self._storage.update(
            {key.lower(): [key, value] for key, value in headers.items()}
        )

    def copy(self):
        """Returns a copy of the headers."""
        return Headers(dict(self._storage.values()))

    def __getitem__(self, name: str):
        return self._storage[name.lower()][1]

    def __setitem__(self, name: str, value: str):
        self._storage[name.lower()] = [name, value]

    def __delitem__(self, name: str):
        del self._storage[name.lower()]

    def __iter__(self):
        return iter(dict(self._storage.values()))

    def __len__(self):
        return len(self._storage)

    def __contains__(self, key: str):
        return key.lower() in self._storage.keys()

    def __repr__(self):
        return f"{self.__class__.__name__}({dict(self._storage.values())})"
