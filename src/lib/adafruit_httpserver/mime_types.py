# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.mime_types`
====================================================
* Author(s): Michał Pokusa
"""

try:
    from typing import List, Dict
except ImportError:
    pass


class MIMETypes:
    """
    Contains MIME types for common file extensions.
    Allows to set default type for unknown files, unregister unused types and register new ones
    using the ``MIMETypes.configure()``.
    """

    DEFAULT = "text/plain"
    """
    Default MIME type for unknown files.
    Can be changed using ``MIMETypes.configure(default_to=...)``.
    """

    REGISTERED = {
        ".7z": "application/x-7z-compressed",
        ".aac": "audio/aac",
        ".abw": "application/x-abiword",
        ".arc": "application/x-freearc",
        ".avi": "video/x-msvideo",
        ".azw": "application/vnd.amazon.ebook",
        ".bin": "application/octet-stream",
        ".bmp": "image/bmp",
        ".bz": "application/x-bzip",
        ".bz2": "application/x-bzip2",
        ".cda": "application/x-cdf",
        ".csh": "application/x-csh",
        ".css": "text/css",
        ".csv": "text/csv",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".eot": "application/vnd.ms-fontobject",
        ".epub": "application/epub+zip",
        ".gif": "image/gif",
        ".gz": "application/gzip",
        ".htm": "text/html",
        ".html": "text/html",
        ".ico": "image/vnd.microsoft.icon",
        ".ics": "text/calendar",
        ".jar": "application/java-archive",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".js": "text/javascript",
        ".json": "application/json",
        ".jsonld": "application/ld+json",
        ".mid": "audio/midi",
        ".midi": "audio/midi",
        ".mjs": "text/javascript",
        ".mp3": "audio/mpeg",
        ".mp4": "video/mp4",
        ".mpeg": "video/mpeg",
        ".mpkg": "application/vnd.apple.installer+xml",
        ".odp": "application/vnd.oasis.opendocument.presentation",
        ".ods": "application/vnd.oasis.opendocument.spreadsheet",
        ".odt": "application/vnd.oasis.opendocument.text",
        ".oga": "audio/ogg",
        ".ogv": "video/ogg",
        ".ogx": "application/ogg",
        ".opus": "audio/opus",
        ".otf": "font/otf",
        ".pdf": "application/pdf",
        ".php": "application/x-httpd-php",
        ".png": "image/png",
        ".ppt": "application/vnd.ms-powerpoint",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".rar": "application/vnd.rar",
        ".rtf": "application/rtf",
        ".sh": "application/x-sh",
        ".svg": "image/svg+xml",
        ".swf": "application/x-shockwave-flash",
        ".tar": "application/x-tar",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
        ".ts": "video/mp2t",
        ".ttf": "font/ttf",
        ".txt": "text/plain",
        ".vsd": "application/vnd.visio",
        ".wav": "audio/wav",
        ".weba": "audio/webm",
        ".webm": "video/webm",
        ".webp": "image/webp",
        ".woff": "font/woff",
        ".woff2": "font/woff2",
        ".xhtml": "application/xhtml+xml",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xml": "application/xml",
        ".xul": "application/vnd.mozilla.xul+xml",
        ".zip": "application/zip",
    }

    @staticmethod
    def __check_all_start_with_dot(extensions: List[str]) -> None:
        for extension in extensions:
            if not extension.startswith("."):
                raise ValueError(
                    f'Invalid extension: "{extension}". All extensions must start with a dot.'
                )

    @classmethod
    def __check_all_are_registered(cls, extensions: List[str]) -> None:
        registered_extensions = cls.REGISTERED.keys()

        for extension in extensions:
            if not extension in registered_extensions:
                raise ValueError(f'Extension "{extension}" is not registered. ')

    @classmethod
    def _default_to(cls, mime_type: str) -> None:
        """
        Set the default MIME type for unknown files.

        :param str mime_type: The MIME type to use for unknown files.
        """
        cls.DEFAULT = mime_type

    @classmethod
    def _keep_for(cls, extensions: List[str]) -> None:
        """
        Unregisters all MIME types except the ones for the given extensions,\
        **decreasing overall memory usage**.
        """

        cls.__check_all_start_with_dot(extensions)
        cls.__check_all_are_registered(extensions)

        current_extensions = iter(cls.REGISTERED.keys())

        cls.REGISTERED = {
            extension: cls.REGISTERED[extension]
            for extension in current_extensions
            if extension in extensions
        }

    @classmethod
    def _register(cls, mime_types: dict) -> None:
        """
        Register multiple MIME types.

        :param dict mime_types: A dictionary mapping file extensions to MIME types.
        """
        cls.__check_all_start_with_dot(mime_types.keys())
        cls.REGISTERED.update(mime_types)

    @classmethod
    def configure(
        cls,
        default_to: str = None,
        keep_for: List[str] = None,
        register: Dict[str, str] = None,
    ) -> None:
        """
        Allows to globally configure the MIME types.

        It is recommended to **always** call this method before starting the ``Server``.
        Unregistering unused MIME types will **decrease overall memory usage**.

        :param str default_to: The MIME type to use for unknown files.
        :param List[str] keep_for: File extensions to keep. All other will be unregistered.
        :param Dict[str, str] register: A dictionary mapping file extensions to MIME types.

        Example::

            MIMETypes.configure(
                default_to="text/plain",
                keep_for=[".jpg", ".mp4", ".txt"],
                register={".foo": "text/foo", ".bar": "text/bar", ".baz": "text/baz"},
            )
        """
        if default_to is not None:
            cls._default_to(default_to)
        if keep_for is not None:
            cls._keep_for(keep_for)
        if register is not None:
            cls._register(register)

    @classmethod
    def get_for_filename(cls, filename: str, default: str = None) -> str:
        """
        Return the MIME type for the given file name.
        If the file extension is not registered, ``default`` is returned.

        :param str filename: The file name to look up.
        :param str default: Default MIME type to return if the file extension is not registered.
        """
        if default is None:
            default = cls.DEFAULT

        try:
            extension = filename.rsplit(".", 1)[-1].lower()
            return cls.REGISTERED.get(f".{extension}", default)
        except IndexError:
            return default
