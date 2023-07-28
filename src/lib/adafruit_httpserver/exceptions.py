# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.exceptions`
====================================================
* Author(s): Michał Pokusa
"""


class ServerStoppedError(Exception):
    """
    Raised when ``.poll`` is called on a stopped ``Server``.
    """


class AuthenticationError(Exception):
    """
    Raised by ``require_authentication`` when the ``Request`` is not authorized.
    """


class InvalidPathError(Exception):
    """
    Parent class for all path related errors.
    """


class ParentDirectoryReferenceError(InvalidPathError):
    """
    Path contains ``..``, a reference to the parent directory.
    """

    def __init__(self, path: str) -> None:
        """Creates a new ``ParentDirectoryReferenceError`` for the ``path``."""
        super().__init__(f"Parent directory reference in path: {path}")


class BackslashInPathError(InvalidPathError):
    """
    Backslash ``\\`` in path.
    """

    def __init__(self, path: str) -> None:
        """Creates a new ``BackslashInPathError`` for the ``path``."""
        super().__init__(f"Backslash in path: {path}")


class ServingFilesDisabledError(Exception):
    """
    Raised when ``root_path`` is not set and there is no handler for ``request``.
    """


class FileNotExistsError(Exception):
    """
    Raised when a file does not exist.
    """

    def __init__(self, path: str) -> None:
        """
        Creates a new ``FileNotExistsError`` for the file at ``path``.
        """
        super().__init__(f"File does not exist: {path}")
