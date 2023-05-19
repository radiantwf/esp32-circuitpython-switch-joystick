# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.route._HTTPRoute`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""

try:
    from typing import Callable, List, Union, Tuple
except ImportError:
    pass

import re

from .methods import HTTPMethod


class _HTTPRoute:
    """Route definition for different paths, see `adafruit_httpserver.server.HTTPServer.route`."""

    def __init__(self, path: str = "", method: HTTPMethod = HTTPMethod.GET) -> None:

        contains_parameters = re.search(r"<\w*>", path) is not None

        self.path = (
            path if not contains_parameters else re.sub(r"<\w*>", r"([^/]*)", path)
        )
        self.method = method
        self._contains_parameters = contains_parameters

    def match(self, other: "_HTTPRoute") -> Tuple[bool, List[str]]:
        """
        Checks if the route matches the other route.

        If the route contains parameters, it will check if the ``other`` route contains values for
        them.

        Returns tuple of a boolean and a list of strings. The boolean indicates if the routes match,
        and the list contains the values of the url parameters from the ``other`` route.

        Examples::

            route = _HTTPRoute("/example", HTTPMethod.GET)

            other1 = _HTTPRoute("/example", HTTPMethod.GET)
            route.matches(other1) # True, []

            other2 = _HTTPRoute("/other-example", HTTPMethod.GET)
            route.matches(other2) # False, []

            ...

            route = _HTTPRoute("/example/<parameter>", HTTPMethod.GET)

            other1 = _HTTPRoute("/example/123", HTTPMethod.GET)
            route.matches(other1) # True, ["123"]

            other2 = _HTTPRoute("/other-example", HTTPMethod.GET)
            route.matches(other2) # False, []
        """

        if self.method != other.method:
            return False, []

        if not self._contains_parameters:
            return self.path == other.path, []

        regex_match = re.match(self.path, other.path)
        if regex_match is None:
            return False, []

        return True, regex_match.groups()

    def __repr__(self) -> str:
        return f"_HTTPRoute(path={repr(self.path)}, method={repr(self.method)})"


class _HTTPRoutes:
    """A collection of routes and their corresponding handlers."""

    def __init__(self) -> None:
        self._routes: List[_HTTPRoute] = []
        self._handlers: List[Callable] = []

    def add(self, route: _HTTPRoute, handler: Callable):
        """Adds a route and its handler to the collection."""

        self._routes.append(route)
        self._handlers.append(handler)

    def find_handler(self, route: _HTTPRoute) -> Union[Callable, None]:
        """
        Finds a handler for a given route.

        If route used URL parameters, the handler will be wrapped to pass the parameters to the
        handler.

        Example::

            @server.route("/example/<my_parameter>", HTTPMethod.GET)
            def route_func(request, my_parameter):
                ...
                request.path == "/example/123" # True
                my_parameter == "123" # True
        """
        if not self._routes:
            return None

        found_route, _route = False, None

        for _route in self._routes:
            matches, url_parameters_values = _route.match(route)

            if matches:
                found_route = True
                break

        if not found_route:
            return None

        handler = self._handlers[self._routes.index(_route)]

        def wrapped_handler(request):
            return handler(request, *url_parameters_values)

        return wrapped_handler

    def __repr__(self) -> str:
        return f"_HTTPRoutes({repr(self._routes)})"
