# ha-nbe-v16 – Home Assistant Integration for NBE V16 Pellet Boiler

[![GitHub Release](https://img.shields.io/github/release/DerT94/ha-nbe-v16.svg)](https://github.com/DerT94/ha-nbe-v16/releases)

A local-push Home Assistant integration for the **NBE V16 pellet boiler** via the **EP20 communication module**.

> ⚠️ **Work in Progress** – This integration is under active development. Expect breaking changes. Not yet ready for production use.

## Features

- 🔥 **100% local** – no cloud, no NBE servers
- 📡 **Push-based** – the EP20 sends data directly to Home Assistant via HTTP POST
- 🌡️ Real-time sensor updates for all Z-values transmitted by the EP20
- ⚡ Push-driven updates via `DataUpdateCoordinator` (no polling)
- 🇩🇪 🇬🇧 German & English translations
- ⚙️ **UI Configuration** – Easy setup via Home Assistant UI (Config Flow)
- 🔀 **Multiple boilers** – each boiler is a separate config entry with its own URL path

## How it works

The EP20 module runs in **Always mode** and sends HTTP POST requests directly to Home Assistant.
The integration receives these requests via a registered `HomeAssistantView` (`api.py`), parses the Z-values from the request body, and distributes them to sensor entities through a `DataUpdateCoordinator`.

The POST body contains one or more embedded GET-style request strings separated by the stop marker `???`:
```
POST /nbe/boiler1/ HTTP/1.0
Content-Length: ...

GET /v16dev/opr.php?mac=XXXXX&z00=0&z01=0&z02=502... HTTP/1.1
Host: stokercloud.dk

???
```

Only `/v16dev/opr.php` blocks are processed; `/v16dev/setup.php` blocks are intentionally ignored.

> **Note on Burst mode:** Burst mode was tested but could not be captured. The EP20 appears to use a challenge-response pattern in Burst mode – it waits for a specific server greeting before sending data. Since the expected greeting is unknown, Burst mode is not supported. Use **Always mode** instead.

### EP20 Configuration

| Setting | Value |
|---|---|
| Protocol | `Http` |
| Server | HA IP address |
| Server Port | `8123` |
| Connect Mode | `Always` |
| Method | `POST` |
| Path | `/nbe/<your-suffix>/` (configured during setup) |

The URL suffix (e.g. `boiler1`) is freely configurable per boiler during the HA Config Flow setup.

## Current Status

### Phase 1 – Architecture & Blueprint ✅
The integration is built upon the modern `integration_blueprint`. The `manifest.json` is ready, and the repository is structured for HACS compatibility.

### Phase 2 – PoC: Data Reception ✅
A working proof-of-concept successfully receives HTTP POST requests from the EP20, parses Z-values from the request body, and sets them as HA states. Transport is HTTP via the HA built-in web server using `HomeAssistantView`.

### Phase 3 – Production Structure ✅
The PoC has been migrated into the full production structure:
- `api.py` – `EP20View` (`HomeAssistantView` subclass) with Z-value parser
- `coordinator.py` – push-driven `NbeDataUpdateCoordinator` using `async_set_updated_data()`
- `config_flow.py` – two-step UI config flow (URL suffix + EP20 setup instructions)
- `entity.py` – shared `NbeEntity` base class with `DeviceInfo`
- `sensor.py` – dynamic raw `NbeRawSensor` entities, one per Z-key

### Phase 4 – Decoded Sensors & Z-value Metadata ⏳
Replace raw sensors with properly decoded, named sensor entities based on a Z-value metadata table in `const.py`.

## File Status

| File | Status | Notes |
|---|---|---|
| `manifest.json` | ✅ Done | Hub integration, local push |
| `__init__.py` | ✅ Done | Setup & teardown of config entries |
| `config_flow.py` | ✅ Done | Two-step UI config flow |
| `api.py` | ✅ Done | `EP20View`, Z-value parser |
| `coordinator.py` | ✅ Done | Push-driven coordinator |
| `entity.py` | ✅ Done | Shared base entity with `DeviceInfo` |
| `sensor.py` | ✅ Done | Dynamic raw Z-value sensors (Phase 3) |
| `const.py` | ⏳ In Progress | Z-value metadata table (Phase 4) |
| `binary_sensor.py` | ⏳ Pending | Binary sensors for boolean Z-values |
| `switch.py` | ⏳ Pending | Control entities for writable Z-values |

## Next Steps

### Must Have
- [ ] **`const.py`** – Define Z-value metadata table: names, units, scaling factors, platform mapping
- [ ] **`sensor.py`** – Replace raw sensors with decoded, named `SensorEntity` classes
- [ ] **`binary_sensor.py`** – Implement binary sensors for boolean-type Z-values

### Nice to Have
- [ ] **`switch.py`** – Control entities for writable EP20 functions
- [ ] **Translations** – Complete `en.json` for all entity names and states

## License

MIT License