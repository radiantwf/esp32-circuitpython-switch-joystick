# SPDX-FileCopyrightText: 2022 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_ntp`
================================================================================

Network Time Protocol (NTP) helper for CircuitPython

 * Author(s): Scott Shawcroft

Implementation Notes
--------------------
**Hardware:**
**Software and Dependencies:**

 * Adafruit CircuitPython firmware for the supported boards:
   https://github.com/adafruit/circuitpython/releases

"""
import struct
import time

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_NTP.git"

NTP_TO_UNIX_EPOCH = 2208988800  # 1970-01-01 00:00:00


class NTP:
    """Network Time Protocol (NTP) helper module for CircuitPython.
    This module does not handle daylight savings or local time. It simply requests
    UTC from a NTP server.
    """

    def __init__(
        self,
        socketpool,
        *,
        server: str = "0.adafruit.pool.ntp.org",
        port: int = 123,
        tz_offset: int = 0,
        socket_timeout: int = 10,
    ) -> None:
        """
        :param object socketpool: A socket provider such as CPython's `socket` module.
        :param str server: The domain of the ntp server to query.
        :param int port: The port of the ntp server to query.
        :param float tz_offset: Timezone offset in hours from UTC. Only useful for timezone ignorant
            CircuitPython. CPython will determine timezone automatically and adjust (so don't use
            this.) For example, Pacific daylight savings time is -7.
        :param int socket_timeout: UDP socket timeout, in seconds.
        """
        self._pool = socketpool
        self._server = server
        self._port = port
        self._packet = bytearray(48)
        self._tz_offset = tz_offset * 60 * 60
        self._socket_timeout = socket_timeout

        # This is our estimated start time for the monotonic clock. We adjust it based on the ntp
        # responses.
        self._monotonic_start = 0

        self.next_sync = 0

    @property
    def datetime(self) -> time.struct_time:
        """Current time from NTP server. Accessing this property causes the NTP time request,
        unless there has already been a recent request. Raises OSError exception if no response
        is received within socket_timeout seconds"""
        if time.monotonic_ns() > self.next_sync:
            self._packet[0] = 0b00100011  # Not leap second, NTP version 4, Client mode
            for i in range(1, len(self._packet)):
                self._packet[i] = 0
            with self._pool.socket(self._pool.AF_INET, self._pool.SOCK_DGRAM) as sock:
                sock.settimeout(self._socket_timeout)
                sock.sendto(self._packet, (self._server, self._port))
                sock.recvfrom_into(self._packet)
                # Get the time in the context to minimize the difference between it and receiving
                # the packet.
                destination = time.monotonic_ns()
            poll = struct.unpack_from("!B", self._packet, offset=2)[0]
            self.next_sync = destination + (2**poll) * 1_000_000_000
            seconds = struct.unpack_from(
                "!I", self._packet, offset=len(self._packet) - 8
            )[0]
            self._monotonic_start = (
                seconds
                + self._tz_offset
                - NTP_TO_UNIX_EPOCH
                - (destination // 1_000_000_000)
            )

        return time.localtime(
            time.monotonic_ns() // 1_000_000_000 + self._monotonic_start
        )
