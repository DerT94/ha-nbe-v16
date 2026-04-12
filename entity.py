"""NbeEntity base class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import NbeDataUpdateCoordinator


class NbeEntity(CoordinatorEntity[NbeDataUpdateCoordinator]):
    """Base entity for NBE V16 – provides shared DeviceInfo for all platforms."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: NbeDataUpdateCoordinator) -> None:
        """Initialize base entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="NBE V16 Pellet Boiler",
            manufacturer="NBE",
            model="V16",
        )