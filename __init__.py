"""NBE V16 Pellet Boiler integration."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import Event, HomeAssistant

from .api import EP20Client
from .const import CONF_HOST, CONF_PORT, DOMAIN, LOGGER
from .coordinator import NbeDataUpdateCoordinator

if TYPE_CHECKING:
    from .data import NbeConfigEntry


PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: NbeConfigEntry) -> bool:
    """Set up NBE V16 integration from a config entry."""
    LOGGER.debug("NBE V16: Setting up entry %s", entry.entry_id)

    coordinator = NbeDataUpdateCoordinator(hass)
    coordinator.config_entry = entry
    entry.runtime_data = coordinator

    # Set data BEFORE async_forward_entry_setups() so coordinator.data is not
    # None when CoordinatorEntity instances register themselves. This prevents
    # any implicit async_request_refresh() from being scheduled.
    coordinator.async_set_updated_data({})

    host: str = entry.data[CONF_HOST]
    port: int = int(entry.data[CONF_PORT])

    client = EP20Client(host=host, port=port, coordinator=coordinator)

    reader_task: asyncio.Task[None] | None = None
    _stop_called = False

    async def _async_stop_reader() -> None:
        """Shut down the TCP reader cleanly on unload.

        Idempotent – safe to call multiple times (e.g. from both the
        HA-stop event listener and async_on_unload).
        """
        nonlocal _stop_called
        if _stop_called:
            return
        _stop_called = True

        if reader_task is not None:
            await client.stop()
            reader_task.cancel()
            try:
                await asyncio.wait_for(reader_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

        LOGGER.debug("NBE V16: TCP reader stopped for entry %s", entry.entry_id)

    entry.async_on_unload(_async_stop_reader)

    async def _async_on_ha_stop(event: Event) -> None:  # noqa: ARG001
        await _async_stop_reader()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_on_ha_stop)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Use async_create_background_task() instead of async_create_task().
    # hass.async_create_task() registers the task in HA's startup job tracker,
    # causing HA to wait for the task to finish before transitioning from
    # STARTING to RUNNING. A persistent TCP reader never finishes by design,
    # so this would block HA startup indefinitely.
    # async_create_background_task() runs the task on the event loop without
    # being tracked as a startup job. The task is automatically cancelled when
    # the config entry is unloaded.
    reader_task = entry.async_create_background_task(
        hass,
        client.run(),
        name=f"{DOMAIN}_reader_{entry.entry_id}",
    )

    LOGGER.info(
        "NBE V16: TCP reader started for %s:%s (entry: %s)",
        host,
        port,
        entry.entry_id,
    )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: NbeConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: NbeConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)