"""Constants for nbe_v16."""
from __future__ import annotations

from dataclasses import dataclass
from logging import Logger, getLogger
from typing import Final

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

# TCP connection timeout in seconds
CONNECT_TIMEOUT = 15

# readline() timeout in seconds
READ_TIMEOUT = 60


# ---------------------------------------------------------------------------
# Z-value metadata
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ZValueMeta:
    """Metadata for a single Z-value sensor."""

    key: str
    """Z-key as it appears in the raw frame, e.g. 'z02'."""

    name: str
    """Human-readable entity name (used as HA entity name)."""

    unit: str | None
    """Unit of measurement, or None."""

    scale: float
    """Divide raw integer by this factor to get the real value."""

    device_class: str | None
    """HA SensorDeviceClass string, or None."""

    state_class: str | None
    """HA SensorStateClass string, or None."""

    enabled_by_default: bool = True
    """False for duplicate Z-keys, disabled in HA by default."""

    duplicate_of: str | None = None
    """Primary key this entry duplicates, if any."""

    lookup: dict[int, str] | None = None
    """Optional int→string lookup table for enum/status Z-values."""


_SUBSTATE_LOOKUP: Final[dict[int, str]] = {
    2: "Ignition preheat",
    6: "Extinguish and cool",
    10: "Boiler valve 1 activate",
    11: "Boiler valve 2 wait",
    12: "Boiler valve 2 activate",
    13: "Burner valve wait",
    14: "Burner valve activate",
    15: "External contact",
    16: "Compressor cleaning",
    17: "Compressor start",
    18: "Pressure reached",
    19: "Burner valve active",
    20: "Pressurising",
    21: "Boiler valve 1 active",
    22: "Compressor depressurising",
    208: "Low boiler temperature",
    211: "Do not restart before problem is found",
    212: "Burner plug or sensor disconnected",
    215: "No connection to boiler temperature sensor",
    217: "Check connections on plug or burner",
    220: "No fire – out of pellets?",
}


Z_VALUE_METADATA: Final[tuple[ZValueMeta, ...]] = (
    # Temperatures
    ZValueMeta("z02", "Boiler Temperature", "°C", 10.0, "temperature", "measurement"),
    ZValueMeta("z50", "Boiler Temperature (z50)", "°C", 10.0, "temperature", "measurement", enabled_by_default=False, duplicate_of="z02"),
    ZValueMeta("z60", "Boiler Temperature (z60)", "°C", 10.0, "temperature", "measurement", enabled_by_default=False, duplicate_of="z02"),
    ZValueMeta("z03", "Drop Shaft Temperature", "°C", 10.0, "temperature", "measurement"),
    ZValueMeta("z04", "Flue Gas Temperature", "°C", 10.0, "temperature", "measurement"),
    ZValueMeta("z25", "Boiler Setpoint", "°C", 10.0, "temperature", "measurement"),
    ZValueMeta("z124", "Outdoor Temperature", "°C", 10.0, "temperature", "measurement"),

    # Power
    ZValueMeta("z00", "Power", "%", 1.0, None, "measurement"),
    ZValueMeta("z59", "Power (z59)", "%", 1.0, None, "measurement", enabled_by_default=False, duplicate_of="z00"),
    ZValueMeta("z01", "Power Output", "kW", 10.0, "power", "measurement"),

    # Oxygen
    ZValueMeta("z05", "Oxygen", "%", 10.0, None, "measurement"),
    ZValueMeta("z70", "Oxygen (z70)", "%", 10.0, None, "measurement", enabled_by_default=False, duplicate_of="z05"),
    ZValueMeta("z24", "Oxygen Setpoint", "%", 10.0, None, "measurement"),
    ZValueMeta("z71", "Oxygen Setpoint (z71)", "%", 10.0, None, "measurement", enabled_by_default=False, duplicate_of="z24"),

    # O2 regulation thresholds
    ZValueMeta("z82", "Oxygen Regulation Low", "%", 100.0, None, "measurement"),
    ZValueMeta("z83", "Oxygen Regulation Mid", "%", 100.0, None, "measurement"),
    ZValueMeta("z84", "Oxygen Regulation High", "%", 100.0, None, "measurement"),

    # Hopper
    ZValueMeta("z18", "Hopper Content", "%", 1.0, None, "measurement"),

    # Consumption
    ZValueMeta("z158", "Consumption 24h", "kg", 10.0, None, "measurement"),
    ZValueMeta("z159", "Consumption Total", "kg", 1.0, None, "total_increasing"),

    # Fan
    ZValueMeta("z121", "Fan Speed", "%", 1.0, None, "measurement"),
    ZValueMeta("z96", "Fan RPM", "rpm", 1.0, None, "measurement"),

    # Combustion chamber
    ZValueMeta("z123", "Combustion Chamber Pressure", "Pa", 1.0, "pressure", "measurement"),

    # Cycle timer
    ZValueMeta("z111", "Cycle Runtime", "s", 1.0, "duration", "measurement"),

    # Status / Enum
    ZValueMeta("z40", "Substate", None, 1.0, None, None, lookup=_SUBSTATE_LOOKUP),
)

Z_VALUE_MAP: Final[dict[str, ZValueMeta]] = {m.key: m for m in Z_VALUE_METADATA}