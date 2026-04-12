"""Custom types for nbe_v16."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import NbeDataUpdateCoordinator


type NbeConfigEntry = ConfigEntry[NbeDataUpdateCoordinator]
