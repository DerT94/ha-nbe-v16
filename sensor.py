"""Sensor platform for nbe_v16."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_DEVELOPER_MODE,
    DOMAIN,
    LOGGER,
    Z_VALUE_MAP,
    Z_VALUE_METADATA,
    ZValueMeta,
)
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
    developer_mode = entry.data.get(CONF_DEVELOPER_MODE, False)
    metadata = {
        meta.key: meta for meta in Z_VALUE_METADATA
        if developer_mode or meta.enabled_by_default
    }
    registry = er.async_get(hass)
    prefix = f"{entry.entry_id}_"
    for registered in er.async_entries_for_config_entry(registry, entry.entry_id):
        if registered.platform != DOMAIN or registered.domain != "sensor":
            continue
        key = registered.unique_id.removeprefix(prefix)
        if not registered.unique_id.startswith(prefix) or not re.fullmatch(r"z[0-9]+", key):
            continue
        if not developer_mode:
            if key not in metadata:
                registry.async_remove(registered.entity_id)
        else:
            # Restore discovered sensors even before the next stream update.
            metadata.setdefault(key, _metadata_for_key(key))
            if registered.disabled_by is er.RegistryEntryDisabler.INTEGRATION:
                registry.async_update_entity(registered.entity_id, disabled_by=None)

    async_add_entities(
        NbeZValueSensor(coordinator, entry, meta, developer_mode=developer_mode)
        for meta in metadata.values()
    )
    if developer_mode:
        known_keys = set(metadata)

        @callback
        def async_discover_z_values() -> None:
            """Create each received Z-key once, including keys arriving later."""
            new_keys = {
                key for key in coordinator.data or {}
                if re.fullmatch(r"z[0-9]+", key) and key not in known_keys
            }
            known_keys.update(new_keys)
            if new_keys:
                async_add_entities(
                    NbeZValueSensor(
                        coordinator, entry, _metadata_for_key(key), developer_mode=True
                    )
                    for key in sorted(new_keys)
                )

        entry.async_on_unload(coordinator.async_add_listener(async_discover_z_values))
        async_discover_z_values()

    LOGGER.debug("NBE V16: sensors registered (developer mode: %s)", developer_mode)


def _metadata_for_key(key: str) -> ZValueMeta:
    """Keep known conversions; expose unidentified fields as unitless raw values."""
    return Z_VALUE_MAP.get(key) or ZValueMeta(key, key, None, 1.0, None, None)


class NbeZValueSensor(NbeEntity, SensorEntity):
    """A single NBE V16 sensor derived from a Z-value metadata entry."""

    _attr_should_poll = False

    def __init__(
        self,
        coordinator: NbeDataUpdateCoordinator,
        entry: NbeConfigEntry,
        meta: ZValueMeta,
        *,
        developer_mode: bool = False,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._meta = meta
        self._attr_unique_id = f"{entry.entry_id}_{meta.key}"
        self.entity_description = SensorEntityDescription(
            key=meta.key,
            name=meta.name,
            translation_key=meta.key,
            native_unit_of_measurement=meta.unit,
            device_class=_device_class(meta),
            state_class=_state_class(meta),
            entity_registry_enabled_default=developer_mode or meta.enabled_by_default,
        )

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

        if self._meta.scale == 1.0:
            return raw_int

        scaled = raw_int / self._meta.scale
        return int(scaled) if scaled == int(scaled) else round(scaled, 2)
