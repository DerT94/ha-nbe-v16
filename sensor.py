"""Sensor platform for nbe_v16."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LOGGER
from .entity import NbeEntity
from .coordinator import NbeDataUpdateCoordinator

if TYPE_CHECKING:
    from .data import NbeConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NbeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: NbeDataUpdateCoordinator = entry.runtime_data
    registered_keys: set[str] = set()

    @callback
    def _async_add_new_sensors(_: Any = None) -> None:
        """Create sensors for any Z-keys not yet registered."""
        if not coordinator.data:
            return

        new_entities = [
            NbeRawSensor(coordinator, key)
            for key in coordinator.data
            if key.startswith("z") and key not in registered_keys
        ]

        if new_entities:
            registered_keys.update(s.z_key for s in new_entities)
            async_add_entities(new_entities)
            LOGGER.info(
                "NBE V16: %d new raw sensor(s) registered: %s",
                len(new_entities),
                [s.z_key for s in new_entities],
            )

    # React to every coordinator update – new Z-keys may arrive at any time
    entry.async_on_unload(
        coordinator.async_add_listener(_async_add_new_sensors)
    )

    LOGGER.info("NBE V16: Sensor platform ready, waiting for first EP20 payload")


class NbeRawSensor(NbeEntity, SensorEntity):
    """A single raw Z-value sensor from the NBE V16 boiler.

    Named sensor.nbe_<key>_raw during Phase 1 (reverse engineering).
    Will be replaced by decoded sensors in Phase 2.
    """

    _attr_should_poll = False

    def __init__(
        self,
        coordinator: NbeDataUpdateCoordinator,
        key: str,
    ) -> None:
        """Initialize the raw sensor."""
        super().__init__(coordinator)
        self.z_key = key
        self._attr_unique_id = f"{DOMAIN}_{coordinator.config_entry.entry_id}_{key}"
        self._attr_name = f"{key.upper()} Raw"

    @property
    def native_value(self) -> str | None:
        """Return current raw value from coordinator data."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.z_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the Z-key as attribute for debugging."""
        return {"z_key": self.z_key}