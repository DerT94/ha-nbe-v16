# ha-nbe-v16 – Home Assistant Integration for NBE V16 Pellet Boiler

[![GitHub Release](https://img.shields.io/github/release/DerT94/ha-nbe-v16.svg)](https://github.com/DerT94/ha-nbe-v16/releases)

A local-push Home Assistant integration for the **NBE V16 pellet boiler** via the **EP20 communication module**.

> ⚠️ **Work in Progress** – This integration is under active development. Expect breaking changes. Not yet ready for production use.

## Planned Features

- 🔥 **100% local** – no cloud, no NBE servers
- 📡 **Push-based** – the EP20 sends data directly to Home Assistant via HTTP Webhooks
- 🌡️ Boiler temperature, flow temperature, flue gas temperature and more
- ⚡ Real-time sensor updates via `DataUpdateCoordinator`
- 🇩🇪 🇬🇧 German & English translations
- ⚙️ **UI Configuration** – Easy setup via Home Assistant UI (Config Flow)

## How it works

The EP20 module runs in **TCP Burst mode** and sends HTTP requests directly to Home Assistant.
The integration intercepts these requests, parses the Z-values, and distributes them to the respective sensor entities.

### EP20 Configuration

| Setting | Value |
|---|---|
| Protocol | HTTP / TCP Client |
| Server | HA IP address |
| Server Port | 8123 (or custom) |
| Connect Mode | Burst |

## Current Status

### Phase 1 – Architecture & Blueprint ✅
The integration is built upon the modern `integration_blueprint`. The `manifest.json` is ready, and the repository is structured for HACS compatibility.

### Phase 2 – Data Reception & Entities ⏳
Currently migrating the raw HTTP listener into the `api.py` and `coordinator.py` structure to dynamically create and update entities.

## File Status

| File | Status | Notes |
|---|---|---|
| `manifest.json` | ✅ Done | Hub integration, local push |
| `config_flow.py`| ⏳ Pending | UI Setup |
| `api.py` | ⏳ Pending | HTTP Request Listener |
| `coordinator.py`| ⏳ Pending | Data management |
| `sensor.py` | ⏳ Pending | Proper HA sensor entities |

## Next Steps

### Must Have 
- [ ] **`config_flow.py`** – Allow user to configure the webhook/port in the UI
- [ ] **`api.py` / `coordinator.py`** – Re-implement the Z-value parser
- [ ] **`const.py`** – Define Z-value table with known names, units, factors
- [ ] **`sensor.py`** – Implement proper `SensorEntity` classes

## License

MIT License