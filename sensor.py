"""Sensor platform for nbe_v16."""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

from .const import LOGGER, Z_VALUE_METADATA, ZValueMeta
from .entity import NbeEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import NbeDataUpdateCoordinator
    from .data import NbeConfigEntry


def _device_class(meta: ZValueMeta) -> SensorDeviceClass | None:
    """Resolve device_class string to SensorDeviceClass enum."""
    if meta.device_class is None:
        return None
    try:
        return SensorDeviceClass(meta.device_class)
    except ValueError:
        return None


def _state_class(meta: ZValueMeta) -> SensorStateClass | None:
    """Resolve state_class string to SensorStateClass enum."""
    if meta.state_class is None:
        return None
    try:
        return SensorStateClass(meta.state_class)
    except ValueError:
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NbeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NBE V16 sensors from a config entry."""
    coordinator: NbeDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        NbeZValueSensor(coordinator, entry, meta)
        for meta in Z_VALUE_METADATA
    )

    LOGGER.debug(
        "NBE V16: %d sensor(s) registered from Z_VALUE_METADATA",
        len(Z_VALUE_METADATA),
    )


class NbeZValueSensor(NbeEntity, SensorEntity):
    """A single NBE V16 sensor derived from a Z-value metadata entry."""

    _attr_should_poll = False

    def __init__(
        self,
        coordinator: NbeDataUpdateCoordinator,
        entry: NbeConfigEntry,
        meta: ZValueMeta,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._meta = meta
        self._attr_unique_id = f"{entry.entry_id}_{meta.key}"
        self._attr_name = meta.name
        self._attr_native_unit_of_measurement = meta.unit
        self._attr_device_class = _device_class(meta)
        self._attr_state_class = _state_class(meta)
        self._attr_entity_registry_enabled_default = meta.enabled_by_default

    @property
    def native_value(self) -> int | float | str | None:
        """Return the current sensor value."""
        data = self.coordinator.data
        if data is None:
            return None

        raw = data.get(self._meta.key)
        if raw is None:
            return None

        try:
            raw_int = int(raw)
        except (ValueError, TypeError):
            return None

        if self._meta.lookup is not None:
            return self._meta.lookup.get(raw_int, f"Unknown ({raw_int})")

        scaled = raw_int / self._meta.scale
        return int(scaled) if scaled == int(scaled) else round(scaled, 2)