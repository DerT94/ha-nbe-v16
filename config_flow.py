"""Config flow for NBE V16 Pellet Boiler."""

from __future__ import annotations

import asyncio

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .api import raw_tcp_settings, validate_raw_tcp_listener
from .const import (
    CONF_DEVELOPER_MODE,
    CONF_HOST,
    CONF_PORT,
    CONF_RAW_TCP_BIND,
    CONF_RAW_TCP_CLIENTS,
    CONF_RAW_TCP_ENABLED,
    CONF_RAW_TCP_PORT,
    DEFAULT_PORT,
    DOMAIN,
    LOGGER,
)

_VALIDATION_CONNECT_TIMEOUT = 5.0
_VALIDATION_CLOSE_TIMEOUT = 2.0


class NbeV16ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for NBE V16."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> NbeRawTCPOptionsFlow:
        """Configure the optional raw TCP socket independently of entity IDs."""
        return NbeRawTCPOptionsFlow()

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
            developer_mode: bool = user_input.get(
                CONF_DEVELOPER_MODE, defaults.get(CONF_DEVELOPER_MODE, False)
            )

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
                            data_updates={
                                CONF_HOST: host, CONF_PORT: port,
                                CONF_DEVELOPER_MODE: developer_mode,
                            },
                            reload_even_if_entry_is_unchanged=False,
                        )
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    LOGGER.debug(
                        "NBE V16: config entry created for %s:%s", host, port
                    )
                    return self.async_create_entry(
                        title=f"NBE V16 Boiler ({host})",
                        data={
                            CONF_HOST: host, CONF_PORT: port,
                            CONF_DEVELOPER_MODE: developer_mode,
                        },
                    )

        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVELOPER_MODE,
                        default=(user_input or defaults).get(CONF_DEVELOPER_MODE, False),
                    ): selector.BooleanSelector(),
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


class NbeRawTCPOptionsFlow(config_entries.OptionsFlow):
    """Explicit opt-in to an unencrypted, IP-restricted raw TCP listener."""

    async def async_step_init(
        self, user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input.get(CONF_RAW_TCP_ENABLED, False):
                try:
                    bind, port, clients = raw_tcp_settings(user_input)
                except (ValueError, TypeError):
                    errors["base"] = "invalid_raw_tcp"
                else:
                    runtime_data = getattr(self.config_entry, "runtime_data", None)
                    active_endpoint = getattr(runtime_data, "raw_tcp_endpoint", None)
                    try:
                        if (bind, port) != active_endpoint:
                            await validate_raw_tcp_listener(bind, port)
                    except OSError:
                        errors["base"] = "raw_tcp_bind_failed"
                    else:
                        return self.async_create_entry(title="", data={
                            CONF_RAW_TCP_ENABLED: True,
                            CONF_RAW_TCP_BIND: bind,
                            CONF_RAW_TCP_PORT: port,
                            CONF_RAW_TCP_CLIENTS: ",".join(sorted(clients)),
                        })
            else:
                return self.async_create_entry(
                    title="", data={**user_input, CONF_RAW_TCP_ENABLED: False}
                )
        values = user_input if user_input is not None else self.config_entry.options
        return self.async_show_form(step_id="init", data_schema=vol.Schema({
            vol.Required(CONF_RAW_TCP_ENABLED, default=values.get(
                CONF_RAW_TCP_ENABLED, False
            )): bool,
            vol.Required(CONF_RAW_TCP_BIND, default=values.get(
                CONF_RAW_TCP_BIND, "127.0.0.1"
            )): str,
            vol.Required(CONF_RAW_TCP_PORT, default=values.get(
                CONF_RAW_TCP_PORT, 2323
            )): vol.All(vol.Coerce(int), vol.Range(min=1024, max=65535)),
            vol.Required(CONF_RAW_TCP_CLIENTS, default=values.get(
                CONF_RAW_TCP_CLIENTS, "127.0.0.1"
            )): str,
        }), errors=errors)
