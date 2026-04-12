"""Binary sensor platform for nbe_v16.

Currently not implemented - placeholder for future binary sensors.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import NbeConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NbeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    # No binary sensors implemented yet
    return
