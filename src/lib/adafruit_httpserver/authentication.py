# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.authentication`
====================================================
* Author(s): Michał Pokusa
"""

try:
    from typing import Union, List
except ImportError:
    pass

from binascii import b2a_base64

from .exceptions import AuthenticationError
from .request import Request


class Basic:
    """Represents HTTP Basic Authentication."""

    def __init__(self, username: str, password: str) -> None:
        self._value = b2a_base64(f"{username}:{password}".encode()).decode().strip()

    def __str__(self) -> str:
        return f"Basic {self._value}"


class Bearer:
    """Represents HTTP Bearer Token Authentication."""

    def __init__(self, token: str) -> None:
        self._value = token

    def __str__(self) -> str:
        return f"Bearer {self._value}"


def check_authentication(request: Request, auths: List[Union[Basic, Bearer]]) -> bool:
    """
    Returns ``True`` if request is authorized by any of the authentications, ``False`` otherwise.

    Example::

        check_authentication(request, [Basic("username", "password")])
    """

    auth_header = request.headers.get("Authorization")

    if auth_header is None:
        return False

    return any(auth_header == str(auth) for auth in auths)


def require_authentication(request: Request, auths: List[Union[Basic, Bearer]]) -> None:
    """
    Checks if the request is authorized and raises ``AuthenticationError`` if not.

    If the error is not caught, the server will return ``401 Unauthorized``.

    Example::

        require_authentication(request, [Basic("username", "password")])
    """

    if not check_authentication(request, auths):
        raise AuthenticationError(
            "Request is not authenticated by any of the provided authentications"
        )
