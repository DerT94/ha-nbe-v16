"""NBE V16 Pellet Boiler integration."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import Event, HomeAssistant

from .api import EP20Client
from .const import CONF_HOST, CONF_PORT, CONF_RAW_TCP_ENABLED, DOMAIN, LOGGER
from .coordinator import NbeDataUpdateCoordinator

if TYPE_CHECKING:
    from .data import NbeConfigEntry


PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: NbeConfigEntry) -> bool:
    """Set up NBE V16 integration from a config entry."""
    LOGGER.debug("NBE V16: Setting up entry %s", entry.entry_id)

    coordinator = NbeDataUpdateCoordinator(hass, entry)
    entry.runtime_data = coordinator

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
        coordinator.raw_tcp_endpoint = None

        await client.stop()
        if reader_task is not None:
            reader_task.cancel()
            try:
                await asyncio.wait_for(reader_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

        LOGGER.debug("NBE V16: TCP reader stopped for entry %s", entry.entry_id)

    entry.async_on_unload(_async_stop_reader)

    async def _async_options_updated(hass: HomeAssistant, updated: NbeConfigEntry) -> None:
        await hass.config_entries.async_reload(updated.entry_id)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    async def _async_on_ha_stop(event: Event) -> None:  # noqa: ARG001
        await _async_stop_reader()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _async_on_ha_stop)
    )

    try:
        if entry.options.get(CONF_RAW_TCP_ENABLED, False):
            try:
                coordinator.raw_tcp_endpoint = await client.start_forwarding(
                    dict(entry.options)
                )
            except (OSError, ValueError, TypeError) as err:
                LOGGER.error(
                    "NBE V16: Raw TCP forwarding failed for entry %s: %s. "
                    "The EP20 reader will still start",
                    entry.entry_id,
                    err,
                )
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except BaseException:
        await _async_stop_reader()
        raise

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

    return True


async def async_unload_entry(hass: HomeAssistant, entry: NbeConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
