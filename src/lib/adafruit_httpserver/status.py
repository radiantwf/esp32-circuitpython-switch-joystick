# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.status`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""


class Status:  # pylint: disable=too-few-public-methods
    """HTTP status code."""

    def __init__(self, code: int, text: str):
        """
        Define a status code.

        :param int code: Numeric value: 200, 404, etc.
        :param str text: Short phrase: "OK", "Not Found', etc.
        """
        self.code = code
        self.text = text

    def __repr__(self):
        return f'Status({self.code}, "{self.text}")'

    def __str__(self):
        return f"{self.code} {self.text}"

    def __eq__(self, other: "Status"):
        return self.code == other.code and self.text == other.text


OK_200 = Status(200, "OK")

CREATED_201 = Status(201, "Created")

ACCEPTED_202 = Status(202, "Accepted")

NO_CONTENT_204 = Status(204, "No Content")

PARTIAL_CONTENT_206 = Status(206, "Partial Content")

TEMPORARY_REDIRECT_307 = Status(307, "Temporary Redirect")

PERMANENT_REDIRECT_308 = Status(308, "Permanent Redirect")

BAD_REQUEST_400 = Status(400, "Bad Request")

UNAUTHORIZED_401 = Status(401, "Unauthorized")

FORBIDDEN_403 = Status(403, "Forbidden")

NOT_FOUND_404 = Status(404, "Not Found")

METHOD_NOT_ALLOWED_405 = Status(405, "Method Not Allowed")

TOO_MANY_REQUESTS_429 = Status(429, "Too Many Requests")

INTERNAL_SERVER_ERROR_500 = Status(500, "Internal Server Error")

NOT_IMPLEMENTED_501 = Status(501, "Not Implemented")

SERVICE_UNAVAILABLE_503 = Status(503, "Service Unavailable")
