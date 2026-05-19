# ha-nbe-v16 – Home Assistant Integration for NBE V16 Pellet Boiler

[

A local Home Assistant integration for the **NBE V16 pellet boiler** via the **EP20 communication module**.

> ⚠️ **Work in Progress** – I am actively developing this integration. Expect breaking changes. It is not yet ready for production use.

## Features

- 🔥 **100% local** – no cloud, no NBE servers
- 📡 **Push-style data flow** – Home Assistant opens a local TCP connection to the EP20 and passively reads the incoming UART stream
- 🌡️ Named, decoded sensors for all known Z-values with correct units and scaling
- ⚡ Push-driven updates via `DataUpdateCoordinator` (no polling loop)
- 🇩🇪 🇬🇧 German & English translations for the config flow
- ⚙️ **UI Configuration** – setup via the Home Assistant UI (Config Flow)
- 🔀 **Multiple boilers** – each boiler is configured as a separate config entry with its own host/port

## How it works

I connect Home Assistant locally to the EP20 **Telnet/TCP port** (default: `23`) and passively read the UART stream exposed by the module. The integration is strictly **read-only** and never sends control commands to the boiler or changes the EP20 configuration.

Incoming UART data contains GET-style request strings separated by the frame marker `???`, for example:

```text
GET /v16dev/opr.php?mac=65506&z000=502&z001=23&z002=0 HTTP/1.1
Host: stokercloud.dk
???
```

I only parse `/v16dev/opr.php` frames for operational Z-values. Frames for `/v16dev/setup.php` and `/v16dev/events2.php` are ignored.

## Available Sensors

All sensors are verified against 25 captured EP20 snapshots (20 operational + 5 standby).
Duplicate Z-keys are exposed as separate entities but **disabled by default** – they can be enabled manually in Home Assistant if needed.

| Sensor | Z-Key | Unit | Notes |
|--------|-------|------|-------|
| Boiler Temperature | z02 | °C | Primary; z50 and z60 are duplicates (disabled) |
| Drop Shaft Temperature | z03 | °C | |
| Flue Gas Temperature | z04 | °C | |
| Power | z00 | % | Primary; z59 is a duplicate (disabled) |
| Power Output | z01 | kW | |
| Oxygen | z05 | % | Primary; z70 is a duplicate (disabled) |
| Oxygen Setpoint | z24 | % | Primary; z71 is a duplicate (disabled) |
| Oxygen Regulation Low | z82 | % | |
| Oxygen Regulation Mid | z83 | % | |
| Oxygen Regulation High | z84 | % | |
| Hopper Content | z18 | % | |
| Consumption 24h | z158 | kg | |
| Consumption Total | z159 | kg | Total increasing counter |
| Fan Speed | z121 | % | |
| Combustion Chamber Pressure | z123 | Pa | |
| Cycle Runtime | z111 | s | Resets on each new burn cycle |

## Why I do not reconfigure the EP20

During earlier experiments, I tested an HTTP-based approach. I observed that the boiler appears to configure or supervise the EP20 via its UART link. If the EP20 behavior does not match what the boiler expects, the boiler/EP20 communication can break and the module may reset.

Because of this, I do **not** attempt to reconfigure the EP20 in any way. This integration only uses the EP20 in its existing setup and passively reads the locally exposed TCP stream.

## EP20 Requirements

The EP20 must be reachable on the local network via its TCP/Telnet port.

| Setting | Value |
|---|---|
| Transport | `TCP` |
| Default Port | `23` |
| Home Assistant role | TCP client |
| EP20 role | TCP server / stream source |
| Data direction | Read-only |

## Current Status

### Phase 1 – TCP stream integration ✅
Persistent local TCP connection to the EP20, parsing incoming `opr.php` frames.

### Phase 2 – Dynamic raw sensors ✅
Raw `SensorEntity` objects created dynamically for Z-values seen in the EP20 stream.

### Phase 3 – Decoded sensors & metadata ✅
Named, decoded sensor entities based on a verified Z-value metadata table in `const.py`.
All known Z-values are mapped to correct names, units, scaling factors, and HA device classes.

### Phase 4 – Diagnostics & tests ⏳
Parser tests, diagnostics support, and MAC-based stable device identifier.

## File Status

| File | Status | Notes |
|---|---|---|
| `manifest.json` | ✅ Done | Config flow enabled, `local_push` |
| `__init__.py` | ✅ Done | Config entry lifecycle, background TCP reader |
| `config_flow.py` | ✅ Done | Host/port UI setup with connection check |
| `api.py` | ✅ Done | Async TCP client and EP20 stream parser |
| `coordinator.py` | ✅ Done | Push-driven coordinator |
| `entity.py` | ✅ Done | Shared base entity with `DeviceInfo` |
| `const.py` | ✅ Done | Z-value metadata table with 21 verified sensors |
| `sensor.py` | ✅ Done | Decoded, named sensors from metadata table |
| `binary_sensor.py` | ⏳ Pending | Optional future typed entities if metadata requires it |

## Next Steps

### Must Have
- [ ] MAC address as stable device identifier
- [ ] Parser tests with captured sample frames

### Nice to Have
- [ ] Diagnostics / debug support for troubleshooting
- [ ] Translations for sensor names when entity names become stable
- [ ] Identify remaining unknown Z-values (z101, z40, z87, z88)

## Important Notes

- This integration is currently **read-only**.
- I do **not** send commands to the EP20.
- I do **not** reconfigure EP20 settings.
- The goal is local monitoring of the NBE V16 pellet boiler.

## License

MIT License