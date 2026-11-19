# NBE V16 for Home Assistant

A local, read-only integration for the NBE V16 pellet boiler through the EP20 UART stream over TCP, normally port 23. Each config entry has its own reader, coordinator and sensors. The integration sends no application data, Telnet negotiation or boiler commands and makes no cloud requests.

**Work in progress. Not released for production use.** No actual Home Assistant target version has completed acceptance. Current local checks use Python 3.12.14 and simulated HA boundaries. They are not a supported-HA version declaration. Real setup/unload, shutdown, availability, translations and recorder compatibility must be verified on a fixed HA version before release.

## Install and configure

1. Obtain this repository from a reviewed revision.
2. In your HA configuration directory, create `custom_components/nbe_v16/`. This repository root is the integration source: copy its root `.py` files, `manifest.json`, `strings.json` and `translations/` there. Do not copy `.git`, `.agents`, `tools` or local test data.
3. Restart Home Assistant to discover the custom integration.
4. Open **Settings → Devices & services → Add integration → NBE V16 Pellet Boiler** and enter the existing EP20 IP address and TCP port.

The check proves TCP reachability only. Sensors remain unavailable until valid measurements arrive. The EP20 must already expose the UART stream as a TCP server; the integration does not reconfigure it. No YAML configuration, cloud account or extra Python runtime package is needed.

To change the address of the **same EP20**, use the entry's **Reconfigure** action. It updates the endpoint and reloads the same entry, preserving its entry ID and sensor unique IDs. An endpoint assigned to another entry is rejected. This does not authenticate a replacement physical device; the stream's `mac` parameter is not treated as a verified Ethernet MAC address.

## Sensors and mapping confidence

There are **25 sensors: 10 enabled by default, 15 disabled**. Twelve disputed fields are unitless, unscaled raw integers and disabled by default. Three further sensors are disabled duplicates. Existing registry choices are retained during updates.

| Enabled sensor | Z-key | Unit / conversion |
| --- | --- | --- |
| Boiler temperature | z02 | °C, raw ÷ 10 |
| Flue gas temperature | z04 | °C, raw ÷ 10 |
| Boiler setpoint | z25 | °C, raw ÷ 10 |
| Outdoor temperature | z124 | °C, raw ÷ 10 |
| Oxygen | z05 | %, raw ÷ 10 |
| Hopper content | z18 | %, raw unchanged |
| Total consumption | z159 | kg, raw unchanged |
| Fan RPM | z96 | rpm, raw unchanged |
| Combustion chamber pressure | z123 | Pa, raw unchanged |
| Substate | z40 | Existing English text; unknown codes retain their number |

The remaining named mappings follow the historical reference, without a fresh independent validation. See [mapping evidence and compatibility](docs/mapping-evidence.md) for disputed keys, missing evidence and statistics implications. Do not infer a physical meaning or unit from a disputed raw field. German and English sensor names are provided; native status values remain unchanged to preserve automation comparisons.

## Update and remove

Before updating, back up HA and review the mapping/statistics compatibility notes. Replace the integration files from one reviewed revision, remove stale integration source files that revision no longer contains, and restart HA. Preserve the configured entry to retain entity identities. Review existing enabled disputed sensors: changing a default does not disable existing registry entries. Old statistics are not converted or deleted automatically.

To remove the integration, delete its entry in **Settings → Devices & services**. After removing all NBE V16 entries, delete only the installed `custom_components/nbe_v16/` directory if no longer needed, then restart HA. Removing an entry does not request erasure of recorder history or statistics.

## Data handling and known limits

- Only operational `/v16dev/opr.php` frames are parsed. Setup, events and unrelated endpoints are ignored. Numeric Z-keys with integer raw values qualify as measurements; MAC-only or malformed payloads do not refresh data.
- `???` completes a frame immediately, including across TCP reads. Clean EOF can complete a syntactically complete request; reset, timeout and cancellation discard unfinished data.
- Frames over 32 KiB are discarded until the next marker. This is a local protection limit, not a documented EP20 maximum.
- Disconnects make data unavailable; valid fresh measurements restore it. Measurements expire after 180 seconds without updates, a provisional limit based on a short passive observation. The independent read timeout is 60 seconds and reconnect delay 10 seconds. Manual refresh does not fetch data or renew its age.
- Valid partial payloads replace previous data; absent keys have no value. Old fields are not merged into new updates.
- Entry diagnostics contain availability, constant limits, counts and known present Z-keys. Endpoint details, MAC, raw values and exception messages are omitted. Debug logs are separate and should be reviewed before sharing.
- Hardware identity, long-term stability, all operating-state transitions and full HA/recorder compatibility remain outside completed local checks. There is no boiler control.

The scripts in [tools/](tools/README.md) are historical, non-passive experiments, not integration dependencies or supported capture tools. Existing formatted example captures are not byte-faithful fixtures. Local harnesses and evidence stay in the gitignored `docs/local-abnahme/` directory under this project's acceptance workflow.

## License

[MIT](LICENSE).
