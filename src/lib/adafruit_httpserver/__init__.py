# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver`
================================================================================

Socket based HTTP Server for CircuitPython


* Author(s): Dan Halbert, Michał Pokusa

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
"""

__version__ = "4.1.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer.git"


from .authentication import (
    Basic,
    Bearer,
    check_authentication,
    require_authentication,
)
from .exceptions import (
    ServerStoppedError,
    AuthenticationError,
    InvalidPathError,
    ParentDirectoryReferenceError,
    BackslashInPathError,
    ServingFilesDisabledError,
    FileNotExistsError,
)
from .headers import Headers
from .methods import (
    GET,
    POST,
    PUT,
    DELETE,
    PATCH,
    HEAD,
    OPTIONS,
    TRACE,
    CONNECT,
)
from .mime_types import MIMETypes
from .request import QueryParams, FormData, Request
from .response import (
    Response,
    FileResponse,
    ChunkedResponse,
    JSONResponse,
    Redirect,
)
from .server import (
    Server,
    NO_REQUEST,
    CONNECTION_TIMED_OUT,
    REQUEST_HANDLED_NO_RESPONSE,
    REQUEST_HANDLED_RESPONSE_SENT,
)
from .status import (
    Status,
    OK_200,
    CREATED_201,
    ACCEPTED_202,
    NO_CONTENT_204,
    PARTIAL_CONTENT_206,
    TEMPORARY_REDIRECT_307,
    PERMANENT_REDIRECT_308,
    BAD_REQUEST_400,
    UNAUTHORIZED_401,
    FORBIDDEN_403,
    NOT_FOUND_404,
    METHOD_NOT_ALLOWED_405,
    TOO_MANY_REQUESTS_429,
    INTERNAL_SERVER_ERROR_500,
    NOT_IMPLEMENTED_501,
    SERVICE_UNAVAILABLE_503,
)
