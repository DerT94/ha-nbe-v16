"""Async TCP client and UART stream parser for nbe_v16."""

from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

from .const import (
    CONNECT_TIMEOUT,
    LOGGER,
    MEASUREMENT_MAX_AGE,
    READ_TIMEOUT,
    RECONNECT_DELAY,
)

if TYPE_CHECKING:
    from .coordinator import NbeDataUpdateCoordinator


# Marker that separates UART frames inside the TCP stream
_FRAME_MARKER = b"???"

# Local safety bound, not a protocol maximum: even 256 Z-value fields at
# 32 bytes each need only 8 KiB, versus 107 fields in the passive capture.
# Allow additional header/noise headroom without accepting unbounded frames.
_MAX_FRAME_BYTES = 32 * 1024
_READ_CHUNK_BYTES = 4096

# Regex to extract a GET request line from a raw UART line.
# The EP20 Telnet port prepends Telnet IAC bytes and sometimes a "login:"
# prompt prefix before the actual HTTP request string. This pattern
# extracts the first occurrence of "GET /v16dev/..." regardless of leading garbage.
_GET_RE = re.compile(r"GET (/v16dev/\S+) HTTP/[0-9]+\.[0-9]+[ \t]*$")

# EP20 endpoint that carries operational Z-value data
_ENDPOINT_OPR = "/v16dev/opr.php"

# EP20 endpoints that are intentionally ignored
_ENDPOINTS_IGNORED = {"/v16dev/events2.php", "/v16dev/setup.php"}

# Keep wire keys unchanged (e.g. z02 and z000); sensor scaling uses integers.
_Z_KEY_RE = re.compile(r"z[0-9]+")
_Z_VALUE_RE = re.compile(r"[+-]?[0-9]+")


class EP20Client:
    """Persistent async TCP client that reads the EP20 UART stream.

    Connects to the EP20 Telnet port and forwards parsed Z-value payloads
    to the coordinator via async_set_updated_data(). Read-only: nothing
    is ever written to the TCP connection.
    """

    def __init__(
        self,
        host: str,
        port: int,
        coordinator: NbeDataUpdateCoordinator,
    ) -> None:
        """Initialize the TCP client."""
        self._host = host
        self._port = port
        self._coordinator = coordinator
        self._running = False
        self._stop_event = asyncio.Event()
        self._writer: asyncio.StreamWriter | None = None
        self._data_timeout: asyncio.TimerHandle | None = None
        self._connection_lost = False

    async def run(self) -> None:
        """Connect to the EP20 and read the UART stream indefinitely.

        Reconnects automatically after a TCP disconnect. Stops only when
        stop() has been called. CancelledError propagates immediately so
        that HA can shut down without delay.
        """
        self._running = True
        self._stop_event.clear()
        while self._running:
            try:
                await self._connect_and_read()
                if self._running:
                    error = ConnectionError("EP20 stream closed")
                    self._invalidate_data(error)
                    self._report_connection_lost(error)
            except asyncio.CancelledError:
                self._invalidate_data(ConnectionError("EP20 reader cancelled"))
                LOGGER.debug("NBE V16: TCP reader task cancelled")
                raise
            except Exception as err:  # noqa: BLE001
                self._invalidate_data(err)
                if not self._running:
                    break
                self._report_connection_lost(err)

            if self._running:
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(), timeout=RECONNECT_DELAY
                    )
                except TimeoutError:
                    pass
                except asyncio.CancelledError:
                    self._invalidate_data(ConnectionError("EP20 reader cancelled"))
                    raise

    def _report_connection_lost(self, error: Exception) -> None:
        """Report one warning per TCP outage, with retry details at DEBUG."""
        if self._connection_lost:
            LOGGER.debug(
                "NBE V16: TCP retry failed for %s:%s (%s)",
                self._host,
                self._port,
                error,
            )
            return
        self._connection_lost = True
        LOGGER.warning(
            "NBE V16: TCP connection to %s:%s lost (%s) - reconnecting in %ds",
            self._host,
            self._port,
            error,
            RECONNECT_DELAY,
        )

    async def stop(self) -> None:
        """Signal the reader loop to stop and close the TCP connection.

        Closing the writer causes the pending reader.read() to return
        immediately with an empty bytes object, which unblocks the read loop
        so the subsequent task.cancel() / await completes without delay.
        """
        self._running = False
        self._stop_event.set()
        self._invalidate_data(ConnectionError("EP20 reader stopped"))
        if self._writer is not None:
            try:
                self._writer.close()
                await asyncio.wait_for(self._writer.wait_closed(), timeout=2.0)
            except Exception:  # noqa: BLE001
                pass
            self._writer = None

    def _invalidate_data(self, error: Exception) -> None:
        """Mark measurements unavailable without replacing the last payload."""
        if self._data_timeout is not None:
            self._data_timeout.cancel()
            self._data_timeout = None
        self._coordinator.async_set_update_error(error)

    def _expire_data(self) -> None:
        """Expire measurements even when unrelated stream traffic continues."""
        self._invalidate_data(TimeoutError("EP20 measurements are stale"))

    async def _connect_and_read(self) -> None:
        """Read bounded UART frames and resynchronize after oversized input.

        A marker completes a frame immediately. Clean EOF also accepts a
        complete request; timeout, reset and cancellation discard any remainder.
        """
        LOGGER.debug(
            "NBE V16: Connecting to EP20 at %s:%s", self._host, self._port
        )
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(self._host, self._port),
            timeout=CONNECT_TIMEOUT,
        )
        self._writer = writer
        if self._connection_lost:
            LOGGER.info(
                "NBE V16: TCP connection to %s:%s restored",
                self._host,
                self._port,
            )
            self._connection_lost = False
        LOGGER.debug(
            "NBE V16: Connected to EP20 at %s:%s - reading stream",
            self._host,
            self._port,
        )

        buffer = b""
        discarding = False
        try:
            while self._running:
                raw = await asyncio.wait_for(
                    reader.read(_READ_CHUNK_BYTES), timeout=READ_TIMEOUT
                )
                if not raw:
                    LOGGER.debug(
                        "NBE V16: TCP connection closed by EP20 (%s:%s)",
                        self._host,
                        self._port,
                    )
                    break

                buffer += raw
                while _FRAME_MARKER in buffer:
                    frame, buffer = buffer.split(_FRAME_MARKER, 1)
                    if not discarding:
                        if len(frame) <= _MAX_FRAME_BYTES:
                            self._process_frame(
                                frame.decode("ascii", errors="replace").splitlines()
                            )
                        else:
                            LOGGER.warning("NBE V16: oversized UART frame discarded")
                    discarding = False

                # Two trailing bytes may be the start of a split marker and
                # therefore do not yet count towards the frame size.
                if len(buffer) > _MAX_FRAME_BYTES + len(_FRAME_MARKER) - 1:
                    if not discarding:
                        LOGGER.warning("NBE V16: oversized UART frame discarded")
                    discarding = True
                if discarding:
                    buffer = buffer[-(len(_FRAME_MARKER) - 1):]
        finally:
            self._writer = None
            try:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=2.0)
            except Exception:  # noqa: BLE001
                pass

        if (
            buffer
            and not discarding
            and len(buffer) <= _MAX_FRAME_BYTES
            and self._running
        ):
            self._process_frame(buffer.decode("ascii", errors="replace").splitlines())

    def _process_frame(self, lines: list[str]) -> None:
        """Identify and parse a complete UART frame.

        Each frame may contain one GET request line, optionally preceded by
        Telnet IAC bytes, a 'login:' prompt, or other noise. We use a regex
        to locate the GET line rather than assuming a fixed line structure.
        """
        for raw_line in lines:
            m = _GET_RE.search(raw_line)
            if m is None:
                continue

            # Extract path without query string
            url_part = m.group(1)              # e.g. /v16dev/opr.php?mac=...
            path = url_part.split("?")[0]      # e.g. /v16dev/opr.php

            if path == _ENDPOINT_OPR:
                # Pass the full url_part directly – no need to reconstruct
                # a GET line that _parse_opr_line would only parse again.
                self._parse_opr_frame(url_part)
                return

            if path in _ENDPOINTS_IGNORED:
                LOGGER.debug("NBE V16: %s frame received - ignored", path)
                return

            LOGGER.debug("NBE V16: unknown endpoint '%s' - ignored", path)
            return

        LOGGER.debug(
            "NBE V16: non-GET frame (header fragment?) - skipped: %s", lines[:2]
        )

    def _parse_opr_frame(self, url_part: str) -> None:
        """Parse Z-values from an opr.php URL part and push to coordinator.

        Receives the URL part directly from _process_frame(), e.g.:
          /v16dev/opr.php?mac=65506&z000=502&z001=0

        Only numeric Z-keys with integer raw values qualify as measurements.
        Ignore frames without measurements so they cannot refresh coordinator data.
        """
        params = parse_qs(urlparse(url_part).query, keep_blank_values=True)

        payload: dict[str, str] = {
            key: values[0]
            for key, values in params.items()
            if _Z_KEY_RE.fullmatch(key) and _Z_VALUE_RE.fullmatch(values[0])
        }

        if not payload:
            LOGGER.warning(
                "NBE V16: opr.php frame without valid Z-values ignored"
            )
            return

        z_count = len(payload)
        if params.get("mac") and params["mac"][0]:
            payload["mac"] = params["mac"][0]

        if self._data_timeout is not None:
            self._data_timeout.cancel()
        self._data_timeout = asyncio.get_running_loop().call_later(
            MEASUREMENT_MAX_AGE, self._expire_data
        )
        self._coordinator.async_set_updated_data(payload)

        LOGGER.debug(
            "NBE V16: opr.php parsed - %d Z-values pushed to coordinator", z_count
        )
