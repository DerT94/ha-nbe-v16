"""DataUpdateCoordinator for nbe_v16."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from .data import NbeConfigEntry


class NbeDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for NBE V16 – push-driven, no polling.

    Data is updated exclusively via async_set_updated_data() when the
    EP20 client receives a new payload. No _async_update_data() is defined
    intentionally – defining it would cause HA to schedule a refresh job
    during async_forward_entry_setups() that never resolves cleanly,
    blocking HA startup indefinitely.
    """

    config_entry: NbeConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            # No update_interval and no _async_update_data – purely push-driven.
        )