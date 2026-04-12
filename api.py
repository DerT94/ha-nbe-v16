"""EP20 HTTP view and payload parser for nbe_v16."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

from aiohttp import web
from homeassistant.components.http import HomeAssistantView

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .coordinator import NbeDataUpdateCoordinator


class EP20View(HomeAssistantView):
    """Receives HTTP POST requests from the NBE EP20 module.

    Each config entry registers its own instance with a unique URL
    and unique view name derived from the entry ID.
    """

    requires_auth = False

    def __init__(
        self,
        url: str,
        entry_id: str,
        coordinator: NbeDataUpdateCoordinator,
    ) -> None:
        """Initialize the view with a unique URL path and entry ID."""
        self.url = url
        self.name = f"{DOMAIN}:ep20:{entry_id}"
        self.coordinator = coordinator

    async def post(self, request: web.Request) -> web.Response:
        """Handle POST request from the EP20 module."""
        body = await request.text()

        LOGGER.debug(
            "NBE V16: POST from %s received\n--- body start ---\n%s\n--- body end ---",
            request.remote,
            body,
        )

        # Body may contain multiple blocks separated by '???'
        for block in body.split("???"):
            block = block.strip()
            if not block:
                continue
            first_line = block.splitlines()[0].strip()
            if "/v16dev/opr.php" in first_line:
                await self._parse_and_process_opr(first_line)
            elif "/v16dev/setup.php" in first_line:
                LOGGER.debug("NBE V16: setup.php received – ignored")
            else:
                LOGGER.debug("NBE V16: unknown block: %s", first_line)

        # EP20 expects a clean 200 OK, otherwise it will retry
        return web.Response(text="OK", status=200)

    async def _parse_and_process_opr(self, line: str) -> None:
        """Parse Z-values from an opr.php GET line and update coordinator.

        Example line:
        GET /v16dev/opr.php?mac=65506&z00=0&z01=0&z02=502 HTTP/1.1
        """
        parts = line.split(" ")
        if len(parts) < 2:
            LOGGER.warning("NBE V16: invalid GET line: %s", line)
            return

        params = parse_qs(urlparse(parts[1]).query)

        payload: dict[str, str] = {
            key: values[0]
            for key, values in params.items()
            if key.startswith("z") or key == "mac"
        }

        if not payload:
            LOGGER.warning("NBE V16: no Z-values found in GET line: %s", line)
            return

        # Push data to coordinator – sensors will update automatically
        self.coordinator.async_set_updated_data(payload)

        z_count = sum(1 for k in payload if k.startswith("z"))
        LOGGER.info("NBE V16: opr.php parsed – %d Z-values processed", z_count)