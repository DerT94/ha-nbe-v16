# ha-nbe-v16 – Home Assistant Integration for NBE V16 Pellet Boiler

[![GitHub Release](https://img.shields.io/github/release/DerT94/ha-nbe-v16.svg)](https://github.com/DerT94/ha-nbe-v16/releases)

A local Home Assistant integration for the **NBE V16 pellet boiler** via the **EP20 communication module**.

> ⚠️ **Work in Progress** – I am actively developing this integration. Expect breaking changes. It is not yet ready for production use.

## Features

- 🔥 **100% local** – no cloud, no NBE servers
- 📡 **Push-style data flow** – Home Assistant opens a local TCP connection to the EP20 and passively reads the incoming UART stream
- 🌡️ Raw sensor creation for transmitted Z-values
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
I have implemented a persistent local TCP connection to the EP20, parse incoming `opr.php` frames, and expose raw Z-values as Home Assistant sensors.

### Phase 2 – Dynamic raw sensors ✅
I currently create raw `SensorEntity` objects dynamically for Z-values seen in the EP20 stream.

### Phase 3 – Decoded sensors & metadata ⏳
Next, I want to replace or complement raw sensors with properly named and decoded entities based on a Z-value metadata table.

## File Status

| File | Status | Notes |
|---|---|---|
| `manifest.json` | ✅ Done | Config flow enabled, `local_push` |
| `__init__.py` | ✅ Done | Config entry lifecycle, background TCP reader |
| `config_flow.py` | ✅ Done | Host/port UI setup with connection check |
| `api.py` | ✅ Done | Async TCP client and EP20 stream parser |
| `coordinator.py` | ✅ Done | Push-driven coordinator |
| `entity.py` | ✅ Done | Shared base entity with `DeviceInfo` |
| `sensor.py` | ✅ Done | Dynamic raw Z-value sensors |
| `const.py` | ⏳ In Progress | Future metadata table for decoded sensors |
| `binary_sensor.py` | ⏳ Pending | Optional future typed entities if metadata requires it |

## Next Steps

### Must Have
- [ ] Define a Z-value metadata table in `const.py`
- [ ] Add decoded, named sensor entities based on known Z-values
- [ ] Improve entity typing, units, and scaling

### Nice to Have
- [ ] Add diagnostics / debug support for troubleshooting
- [ ] Add parser-focused tests with captured sample frames
- [ ] Expand translations when entity names and states become stable

## Important Notes

- This integration is currently **read-only**.
- I do **not** send commands to the EP20.
- I do **not** reconfigure EP20 settings.
- The goal is local monitoring and reverse engineering of Z-values.

## License

MIT License