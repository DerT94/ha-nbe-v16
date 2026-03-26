import logging
from homeassistant.core import HomeAssistant
from homeassistant.components.http import HomeAssistantView
from aiohttp import web

_LOGGER = logging.getLogger(__name__)
DOMAIN = "nbe_v16"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.http.register_view(NBEReportView(hass))
    _LOGGER.info("NBE V16: HTTP endpoint /api/nbe_v16 registered")
    return True


class NBEReportView(HomeAssistantView):
    url = "/api/nbe_v16"
    name = "api:nbe_v16"
    requires_auth = False

    def __init__(self, hass: HomeAssistant):
        self.hass = hass

    async def get(self, request: web.Request) -> web.Response:
        params = request.rel_url.query
        for key, value in params.items():
            if key.startswith("z"):
                entity_id = f"sensor.nbe_{key}_raw"
                self.hass.states.async_set(entity_id, value)
                _LOGGER.debug("NBE V16: %s = %s", entity_id, value)
        return web.Response(text="OK")