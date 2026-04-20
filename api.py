"""Async TCP client and UART stream parser for nbe_v16."""

from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

from .const import CONNECT_TIMEOUT, LOGGER, READ_TIMEOUT, RECONNECT_DELAY

if TYPE_CHECKING:
    from .coordinator import NbeDataUpdateCoordinator


# Marker that separates UART frames inside the TCP stream
_FRAME_MARKER = "???"

# Regex to extract a GET request line from a raw UART line.
# The EP20 Telnet port prepends Telnet IAC bytes and sometimes a "login:"
# prompt prefix before the actual HTTP request string. This pattern
# extracts the first occurrence of "GET /v16dev/..." regardless of leading garbage.
_GET_RE = re.compile(r"GET (/v16dev/\S+) HTTP/")

# EP20 endpoint that carries operational Z-value data
_ENDPOINT_OPR = "/v16dev/opr.php"

# EP20 endpoints that are intentionally ignored
_ENDPOINTS_IGNORED = {"/v16dev/events2.php", "/v16dev/setup.php"}


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
        self._writer: asyncio.StreamWriter | None = None

    async def run(self) -> None:
        """Connect to the EP20 and read the UART stream indefinitely.

        Reconnects automatically after a TCP disconnect. Stops only when
        stop() has been called. CancelledError propagates immediately so
        that HA can shut down without delay.
        """
        self._running = True
        while self._running:
            try:
                await self._connect_and_read()
            except asyncio.CancelledError:
                LOGGER.debug("NBE V16: TCP reader task cancelled")
                raise
            except Exception as err:  # noqa: BLE001
                if not self._running:
                    break
                LOGGER.warning(
                    "NBE V16: TCP connection to %s:%s lost (%s) - reconnecting in %ds",
                    self._host,
                    self._port,
                    err,
                    RECONNECT_DELAY,
                )
                try:
                    await asyncio.sleep(RECONNECT_DELAY)
                except asyncio.CancelledError:
                    LOGGER.debug("NBE V16: reconnect wait cancelled - shutting down")
                    raise

    async def stop(self) -> None:
        """Signal the reader loop to stop and close the TCP connection.

        Closing the writer causes the pending reader.readline() to return
        immediately with an empty bytes object, which unblocks the read loop
        so the subsequent task.cancel() / await completes without delay.
        """
        self._running = False
        if self._writer is not None:
            try:
                self._writer.close()
                await asyncio.wait_for(self._writer.wait_closed(), timeout=2.0)
            except Exception:  # noqa: BLE001
                pass
            self._writer = None

    async def _connect_and_read(self) -> None:
        """Open a TCP connection and read lines until the connection closes."""
        LOGGER.info(
            "NBE V16: Connecting to EP20 at %s:%s", self._host, self._port
        )
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(self._host, self._port),
            timeout=CONNECT_TIMEOUT,
        )
        self._writer = writer
        LOGGER.info(
            "NBE V16: Connected to EP20 at %s:%s - reading stream",
            self._host,
            self._port,
        )

        buffer: list[str] = []
        try:
            while self._running:
                try:
                    raw = await asyncio.wait_for(
                        reader.readline(), timeout=READ_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    # No data received within READ_TIMEOUT – connection is stale.
                    # Log any buffered content that would otherwise be silently
                    # discarded so protocol issues can be diagnosed.
                    if buffer:
                        LOGGER.warning(
                            "NBE V16: READ_TIMEOUT with %d buffered line(s) – "
                            "incomplete frame discarded: %s",
                            len(buffer),
                            buffer[:3],
                        )
                        buffer = []
                    raise

                if not raw:
                    LOGGER.info(
                        "NBE V16: TCP connection closed by EP20 (%s:%s)",
                        self._host,
                        self._port,
                    )
                    break

                line = raw.decode("ascii", errors="replace").rstrip("\r\n")

                if _FRAME_MARKER in line:
                    parts = line.split(_FRAME_MARKER)

                    if parts[0]:
                        buffer.append(parts[0])
                    self._process_frame(buffer)
                    buffer = []

                    for fragment in parts[1:-1]:
                        if fragment:
                            self._process_frame([fragment])

                    remainder = parts[-1]
                    if remainder:
                        buffer.append(remainder)
                else:
                    buffer.append(line)
        finally:
            self._writer = None
            try:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=2.0)
            except Exception:  # noqa: BLE001
                pass

        if buffer:
            self._process_frame(buffer)

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

        No regex needed here – the caller already extracted the clean URL part.
        """
        params = parse_qs(urlparse(url_part).query)

        payload: dict[str, str] = {
            key: values[0]
            for key, values in params.items()
            if key.startswith("z") or key == "mac"
        }

        if not payload:
            LOGGER.warning(
                "NBE V16: no Z-values found in opr.php frame: %s", url_part
            )
            return

        self._coordinator.async_set_updated_data(payload)

        z_count = sum(1 for k in payload if k.startswith("z"))
        LOGGER.debug(
            "NBE V16: opr.php parsed - %d Z-values pushed to coordinator", z_count
        )