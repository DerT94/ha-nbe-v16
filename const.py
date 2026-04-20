"""Constants for nbe_v16."""

from __future__ import annotations

from logging import Logger, getLogger


LOGGER: Logger = getLogger(__package__)

DOMAIN = "nbe_v16"

# Attribution
ATTRIBUTION = "Data provided by NBE V16 Pellet Boiler via EP20 module"

# Device info
DEVICE_NAME = "NBE V16 Pellet Boiler"
DEVICE_MANUFACTURER = "NBE"
DEVICE_MODEL = "V16"

# Config entry keys
CONF_HOST = "host"
CONF_PORT = "port"

# Default TCP connection parameters for the EP20 Telnet port
DEFAULT_PORT = 23

# Reconnect delay in seconds after a TCP connection loss
RECONNECT_DELAY = 10

# TCP connection timeout in seconds – prevents open_connection() from hanging
# indefinitely when the EP20 is temporarily unreachable at startup.
CONNECT_TIMEOUT = 15

# readline() timeout in seconds – prevents the read loop from blocking forever
# if the EP20 stops sending data (e.g. stale TCP connection without RST).
READ_TIMEOUT = 60