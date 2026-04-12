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

    Data is updated via async_set_updated_data() when the EP20 view
    receives a new payload.
    """

    config_entry: NbeConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            # No update_interval – data arrives via push from EP20
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """No polling – data is pushed by the EP20 via async_set_updated_data."""
        return self.data or {}
