"""Switch platform for nbe_v16.

Not implemented yet - placeholder only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .data import NbeConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: NbeConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform - no switches implemented yet."""
    return
