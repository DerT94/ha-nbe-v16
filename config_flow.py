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
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=(user_input or {}).get(CONF_HOST, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(
                        CONF_PORT,
                        default=(user_input or {}).get(CONF_PORT, DEFAULT_PORT),
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
