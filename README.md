# NBE V16 for Home Assistant

A local, read-only integration for NBE V16 pellet boilers through the EP20 UART stream over TCP. It sends no application data, Telnet replies or boiler commands and makes no cloud requests. Each configured endpoint has its own connection, coordinator and sensors.

**Beta candidate 0.1.1b1**, minimum Home Assistant Core **2026.11.2**. Functional acceptance on HA 2026.11.2 / Python 3.14.10 covered setup/unload, shutdown and restart, disconnect/reconnect, stale measurements, developer mode, Recorder and TCP forwarding. Long-term observation and visual dialog verification remain open. This candidate is not a production release. See the [changelog](CHANGELOG.md).

## Install and configure

1. Obtain a reviewed revision of this repository.
2. Create `custom_components/nbe_v16/` in your HA configuration directory. Copy the repository's root `.py` files, `manifest.json`, `strings.json` and `translations/` there.
3. Restart Home Assistant.
4. Open **Settings → Devices & services → Add integration → NBE V16 Pellet Boiler** and enter the EP20 address and TCP port, normally 23.

The EP20 must already expose its UART stream as a TCP server. The setup check proves TCP reachability; sensors become available only after valid measurements arrive. No YAML configuration, cloud account or extra Python runtime package is needed.

## Features and documentation

- **Sensors:** normal mode exposes primary measurements and operating states. See the [sensor reference](docs/sensors.md) for conversions and units.
- **Developer mode:** additionally discovers raw Z-values. [Configuration](docs/configuration.md) explains activation and registry effects.
- **TCP forwarding:** one HA instance can forward its EP20 stream to other readers. Setup and network restrictions are in [configuration](docs/configuration.md#raw-tcp-forwarding).
- **Mapping confidence:** [mapping evidence](docs/mapping-evidence.md) separates established associations, uncertain interpretations and fields that cannot be resolved with the available installation.
- **Technical behavior:** framing, reconnects, availability and forwarding limits are in the [stream reference](docs/ep20-stream.md).

German and English sensor names are available. Native status values remain English to preserve existing automation comparisons. Hardware identity and physical meanings of unknown Z-values are not inferred.

## Update and remove

Before updating, back up HA and read the [compatibility notes](docs/compatibility.md), especially when using developer entities or old statistics. Replace the integration files from one reviewed revision, remove stale source files no longer included, and restart HA. Preserve the configured entry to retain its identity.

To remove the integration, delete its entries in **Settings → Devices & services**. After removing all entries, delete the installed `custom_components/nbe_v16/` directory and restart HA. Removing entries does not request deletion of Recorder history or statistics.

The scripts in [tools/](tools/README.md) are historical experiments with separate networking behavior. Local acceptance material is kept outside version control.

## License

[MIT](LICENSE).
