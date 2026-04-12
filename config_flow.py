"""Config flow for NBE V16 Pellet Boiler."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.loader import async_get_loaded_integration

from .const import CONF_URL_SUFFIX, DEFAULT_URL_SUFFIX, DOMAIN, LOGGER, NBE_PATH_PREFIX


class NbeV16ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for NBE V16."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._url_suffix: str = DEFAULT_URL_SUFFIX

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Step 1: Enter URL suffix."""
        _errors: dict[str, str] = {}

        integration = async_get_loaded_integration(self.hass, DOMAIN)
        assert integration.documentation is not None, (  # noqa: S101
            "Integration documentation URL is not set in manifest.json"
        )

        if user_input is not None:
            url_suffix = user_input[CONF_URL_SUFFIX].strip()
            if not url_suffix:
                _errors[CONF_URL_SUFFIX] = "url_suffix_required"
            else:
                self._url_suffix = url_suffix
                await self.async_set_unique_id(f"nbe_v16_{url_suffix}")
                self._abort_if_unique_id_configured()
                return await self.async_step_instructions()

        return self.async_show_form(
            step_id="user",
            description_placeholders={
                "documentation_url": integration.documentation,
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_URL_SUFFIX,
                        default=(user_input or {}).get(CONF_URL_SUFFIX, DEFAULT_URL_SUFFIX),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                }
            ),
            errors=_errors,
        )

    async def async_step_instructions(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Step 2: Show EP20 configuration instructions, then finish."""
        if user_input is not None:
            LOGGER.debug(
                "NBE V16: config entry created for suffix '%s'", self._url_suffix
            )
            return self.async_create_entry(
                title=f"NBE V16 Boiler ({self._url_suffix})",
                data={CONF_URL_SUFFIX: self._url_suffix},
            )

        url_path = f"{NBE_PATH_PREFIX}{self._url_suffix}/"

        return self.async_show_form(
            step_id="instructions",
            description_placeholders={
                "url_path": url_path,
            },
            data_schema=vol.Schema({}),
        )