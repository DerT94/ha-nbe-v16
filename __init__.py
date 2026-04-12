"""NBE V16 Pellet Boiler integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import EP20View
from .const import CONF_URL_SUFFIX, DOMAIN, LOGGER, NBE_PATH_PREFIX
from .coordinator import NbeDataUpdateCoordinator

if TYPE_CHECKING:
    from .data import NbeConfigEntry

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: NbeConfigEntry) -> bool:
    """Set up NBE V16 integration from a config entry."""
    LOGGER.debug("Setting up NBE V16 entry %s", entry.entry_id)

    coordinator = NbeDataUpdateCoordinator(hass)
    coordinator.config_entry = entry
    entry.runtime_data = coordinator

    url_suffix = entry.data[CONF_URL_SUFFIX]
    url_path = f"{NBE_PATH_PREFIX}{url_suffix}/"

    view = EP20View(url=url_path, entry_id=entry.entry_id, coordinator=coordinator)
    hass.http.register_view(view)

    LOGGER.info(
        "NBE V16: EP20 endpoint registered at %s (entry: %s)",
        url_path,
        entry.entry_id,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: NbeConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: NbeConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)