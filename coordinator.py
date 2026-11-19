"""DataUpdateCoordinator for nbe_v16."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import NbeConfigEntry


class NbeDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for NBE V16 – push-driven, no polling.

    The EP20 reader pushes measurements and reports disconnects or stale data.
    No periodic refresh is scheduled.
    """

    config_entry: NbeConfigEntry

    def __init__(self, hass: HomeAssistant, entry: NbeConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            config_entry=entry,
            # No update_interval: measurements arrive through the reader.
        )
        # A TCP connection alone is not evidence of valid measurements.
        self.last_update_success = False
        self.raw_tcp_endpoint: tuple[str, int] | None = None

    @callback
    def async_set_stopped(self, error: Exception) -> None:
        """Notify unavailability for planned shutdown without an outage log."""
        self.last_exception = error
        if self.last_update_success:
            self.last_update_success = False
            self.async_update_listeners()

    async def async_request_refresh(self) -> None:
        """Accept manual refresh without fetching or validating cached data.

        Only a new EP20 measurement can restore success and renew data age.
        """
