"""Diagnostics with an explicit allowlist of non-identifying metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import MEASUREMENT_MAX_AGE, Z_VALUE_METADATA

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import NbeConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: NbeConfigEntry
) -> dict[str, object]:
    """Describe data availability without exposing endpoint, payload or errors."""
    coordinator = entry.runtime_data
    data = coordinator.data or {}
    return {
        "last_update_success": coordinator.last_update_success,
        "measurement_max_age_seconds": MEASUREMENT_MAX_AGE,
        "configured_sensor_count": len(Z_VALUE_METADATA),
        "enabled_by_default_count": sum(
            meta.enabled_by_default for meta in Z_VALUE_METADATA
        ),
        "present_z_keys": [meta.key for meta in Z_VALUE_METADATA if meta.key in data],
    }
