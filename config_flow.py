"""Config flow for NBE V16 Pellet Boiler."""

from __future__ import annotations

import asyncio

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import CONF_HOST, CONF_PORT, DEFAULT_PORT, DOMAIN, LOGGER

_VALIDATION_CONNECT_TIMEOUT = 5.0
_VALIDATION_CLOSE_TIMEOUT = 2.0


class NbeV16ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for NBE V16."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Enter IP address and TCP port of the EP20 module."""
        return await self._async_step_endpoint(user_input)

    async def async_step_reconfigure(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Change the endpoint while retaining the entry and its entities."""
        return await self._async_step_endpoint(
            user_input, entry=self._get_reconfigure_entry()
        )

    async def _async_step_endpoint(
        self,
        user_input: dict | None,
        *,
        entry: config_entries.ConfigEntry | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Validate an endpoint for setup or reconfiguration."""
        step_id = "reconfigure" if entry is not None else "user"
        defaults = entry.data if entry is not None else {}
        errors: dict[str, str] = {}

        if user_input is not None:
            host: str = user_input[CONF_HOST].strip()
            port: int = int(user_input[CONF_PORT])

            if not host:
                errors[CONF_HOST] = "host_required"
            else:
                try:
                    # This validates TCP reachability, not UART measurements.
                    _, writer = await asyncio.wait_for(
                        asyncio.open_connection(host, port),
                        timeout=_VALIDATION_CONNECT_TIMEOUT,
                    )
                    writer.close()
                    await asyncio.wait_for(
                        writer.wait_closed(), timeout=_VALIDATION_CLOSE_TIMEOUT
                    )
                except TimeoutError:
                    errors["base"] = "cannot_connect"
                except OSError:
                    errors["base"] = "cannot_connect"
                else:
                    unique_id = f"nbe_v16_{host}_{port}"
                    if entry is not None:
                        if any(
                            configured.entry_id != entry.entry_id
                            and (
                                configured.unique_id == unique_id
                                or (
                                    configured.data.get(CONF_HOST) == host
                                    and configured.data.get(CONF_PORT) == port
                                )
                            )
                            for configured in self._async_current_entries()
                        ):
                            return self.async_abort(reason="already_configured")
                        return self.async_update_reload_and_abort(
                            entry,
                            unique_id=unique_id,
                            data_updates={CONF_HOST: host, CONF_PORT: port},
                            reload_even_if_entry_is_unchanged=False,
                        )
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    LOGGER.debug(
                        "NBE V16: config entry created for %s:%s", host, port
                    )
                    return self.async_create_entry(
                        title=f"NBE V16 Boiler ({host})",
                        data={CONF_HOST: host, CONF_PORT: port},
                    )

        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or defaults).get(CONF_HOST, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        CONF_PORT,
                        default=(user_input or defaults).get(CONF_PORT, DEFAULT_PORT),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                }
            ),
            errors=errors,
        )
