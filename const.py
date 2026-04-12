"""Constants for nbe_v16."""

from __future__ import annotations

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "nbe_v16"

# Attribution
ATTRIBUTION = "Data provided by NBE V16 Pellet Boiler via EP20 module"

# Fixed base path prefix; only the suffix is user-configurable
NBE_PATH_PREFIX = "/nbe/"

# Default URL path suffix for the EP20 endpoint
DEFAULT_URL_SUFFIX = "boiler1"

# Config entry key for the user-configurable URL suffix
CONF_URL_SUFFIX = "url_suffix"