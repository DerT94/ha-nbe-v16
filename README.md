# ha-nbe-v16 – Home Assistant Integration for NBE V16 Pellet Boiler

[![GitHub Release](https://img.shields.io/github/release/DerT94/ha-nbe-v16.svg)](https://github.com/DerT94/ha-nbe-v16/releases)

A local-push Home Assistant integration for the **NBE V16 pellet boiler** via the **EP20 communication module**.

> ⚠️ **Work in Progress** – This integration is under active development. Expect breaking changes. Not yet ready for production use.

## Planned Features

- 🔥 **100% local** – no cloud, no NBE servers
- 📡 **Push-based** – the EP20 sends data directly to Home Assistant
- 🌡️ Boiler temperature, flow temperature, flue gas temperature and more
- ⚡ Real-time sensor updates
- 🇩🇪 🇬🇧 German & English translations

## How it works

The EP20 module sends HTTP GET requests directly to Home Assistant.
Home Assistant receives the data, decodes the Z-values and exposes them as sensors.

## Current Repository Status

| File | Status |
|---|---|
| `README.md` | ✅ WIP notice, description |
| `.gitignore` | ✅ Python + HA rules |
| `manifest.json` | ⏳ Empty |
| `__init__.py` | ⏳ Empty |
| `const.py` | ⏳ Empty |
| `sensor.py` | ⏳ Empty |
| `strings.json` | ⏳ Empty |
| `translations/de.json` | ⏳ Empty |
| `translations/en.json` | ⏳ Empty |

## Open Tasks

- [ ] Fill all `.py` files with initial code
- [ ] Configure logger in `configuration.yaml`
- [ ] Reconfigure EP20 to point to DEV IP
- [ ] Create `hacs.json`
- [ ] Documentation

## License

MIT License
