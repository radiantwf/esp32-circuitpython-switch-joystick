# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_httpserver.mime_type.MIMEType`
====================================================
* Author(s): Dan Halbert, Michał Pokusa
"""


class MIMEType:
    """Common MIME types.
    From https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    """

    TYPE_AAC = "audio/aac"
    TYPE_ABW = "application/x-abiword"
    TYPE_ARC = "application/x-freearc"
    TYPE_AVI = "video/x-msvideo"
    TYPE_AZW = "application/vnd.amazon.ebook"
    TYPE_BIN = "application/octet-stream"
    TYPE_BMP = "image/bmp"
    TYPE_BZ = "application/x-bzip"
    TYPE_BZ2 = "application/x-bzip2"
    TYPE_CSH = "application/x-csh"
    TYPE_CSS = "text/css"
    TYPE_CSV = "text/csv"
    TYPE_DOC = "application/msword"
    TYPE_DOCX = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    TYPE_EOT = "application/vnd.ms-fontobject"
    TYPE_EPUB = "application/epub+zip"
    TYPE_GZ = "application/gzip"
    TYPE_GIF = "image/gif"
    TYPE_HTML = "text/html"
    TYPE_HTM = "text/html"
    TYPE_ICO = "image/vnd.microsoft.icon"
    TYPE_ICS = "text/calendar"
    TYPE_JAR = "application/java-archive"
    TYPE_JPEG = "image/jpeg"
    TYPE_JPG = "image/jpeg"
    TYPE_JS = "text/javascript"
    TYPE_JSON = "application/json"
    TYPE_JSONLD = "application/ld+json"
    TYPE_MID = "audio/midi"
    TYPE_MIDI = "audio/midi"
    TYPE_MJS = "text/javascript"
    TYPE_MP3 = "audio/mpeg"
    TYPE_CDA = "application/x-cdf"
    TYPE_MP4 = "video/mp4"
    TYPE_MPEG = "video/mpeg"
    TYPE_MPKG = "application/vnd.apple.installer+xml"
    TYPE_ODP = "application/vnd.oasis.opendocument.presentation"
    TYPE_ODS = "application/vnd.oasis.opendocument.spreadsheet"
    TYPE_ODT = "application/vnd.oasis.opendocument.text"
    TYPE_OGA = "audio/ogg"
    TYPE_OGV = "video/ogg"
    TYPE_OGX = "application/ogg"
    TYPE_OPUS = "audio/opus"
    TYPE_OTF = "font/otf"
    TYPE_PNG = "image/png"
    TYPE_PDF = "application/pdf"
    TYPE_PHP = "application/x-httpd-php"
    TYPE_PPT = "application/vnd.ms-powerpoint"
    TYPE_PPTX = (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )
    TYPE_RAR = "application/vnd.rar"
    TYPE_RTF = "application/rtf"
    TYPE_SH = "application/x-sh"
    TYPE_SVG = "image/svg+xml"
    TYPE_SWF = "application/x-shockwave-flash"
    TYPE_TAR = "application/x-tar"
    TYPE_TIFF = "image/tiff"
    TYPE_TIF = "image/tiff"
    TYPE_TS = "video/mp2t"
    TYPE_TTF = "font/ttf"
    TYPE_TXT = "text/plain"
    TYPE_VSD = "application/vnd.visio"
    TYPE_WAV = "audio/wav"
    TYPE_WEBA = "audio/webm"
    TYPE_WEBM = "video/webm"
    TYPE_WEBP = "image/webp"
    TYPE_WOFF = "font/woff"
    TYPE_WOFF2 = "font/woff2"
    TYPE_XHTML = "application/xhtml+xml"
    TYPE_XLS = "application/vnd.ms-excel"
    TYPE_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    TYPE_XML = "application/xml"
    TYPE_XUL = "application/vnd.mozilla.xul+xml"
    TYPE_ZIP = "application/zip"
    TYPE_7Z = "application/x-7z-compressed"

    @staticmethod
    def from_file_name(filename: str):
        """Return the mime type for the given filename. If not known, return "text/plain"."""
        attr_name = "TYPE_" + filename.split(".")[-1].upper()

        return getattr(MIMEType, attr_name, MIMEType.TYPE_TXT)
