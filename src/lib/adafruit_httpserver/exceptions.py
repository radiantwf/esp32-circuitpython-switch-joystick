# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.exceptions`
====================================================
* Author(s): Michał Pokusa
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


class ResponseAlreadySentError(Exception):
    """
    Another ``HTTPResponse`` has already been sent. There can only be one per ``HTTPRequest``.
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
