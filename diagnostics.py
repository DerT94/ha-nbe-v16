"""Diagnostics with an explicit allowlist of non-identifying metadata."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_DEVELOPER_MODE,
    CONF_RAW_TCP_ENABLED,
    DOMAIN,
    MEASUREMENT_MAX_AGE,
    Z_VALUE_METADATA,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import NbeConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: NbeConfigEntry
) -> dict[str, object]:
    """Describe data availability without exposing endpoint, payload or errors."""
    coordinator = entry.runtime_data
    data = coordinator.data or {}
    developer_mode = entry.data.get(CONF_DEVELOPER_MODE, False)
    forwarding_enabled = entry.options.get(CONF_RAW_TCP_ENABLED, False)
    forwarding_status = (
        "disabled" if not forwarding_enabled else
        "listening" if coordinator.raw_tcp_endpoint is not None else
        "not_listening"
    )
    keys = {
        meta.key for meta in Z_VALUE_METADATA
        if developer_mode or meta.enabled_by_default
    }
    if developer_mode:
        keys.update(key for key in data if re.fullmatch(r"z[0-9]+", key))
        prefix = f"{entry.entry_id}_"
        for registered in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id):
            key = registered.unique_id.removeprefix(prefix)
            if (
                registered.platform == DOMAIN
                and registered.domain == "sensor"
                and registered.unique_id.startswith(prefix)
                and re.fullmatch(r"z[0-9]+", key)
            ):
                keys.add(key)
    return {
        "raw_tcp_forwarding": {
            "enabled": forwarding_enabled,
            "status": forwarding_status,
        },
        "developer_mode": developer_mode,
        "last_update_success": coordinator.last_update_success,
        "measurement_max_age_seconds": MEASUREMENT_MAX_AGE,
        "configured_sensor_count": len(keys),
        "enabled_by_default_count": len(keys),
        "present_z_keys": sorted(keys.intersection(data)),
    }
