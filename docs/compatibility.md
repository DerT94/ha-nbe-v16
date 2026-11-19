# Compatibility and existing installations

The current beta declares Home Assistant Core 2026.11.2 as its minimum version. The [changelog](../CHANGELOG.md) records candidate-specific changes and acceptance limits. These notes describe effects relevant when moving from earlier development revisions.

## Entity identity

Sensor unique IDs use `<config-entry-id>_<z-key>`. Reconfiguring the endpoint of the same EP20 preserves the entry and sensor unique IDs. Endpoint uniqueness uses host/port; no MAC-based migration or physical-device authentication is performed.

## Entity registry and developer mode

Normal mode removes additional Z-value entities belonging to this entry, including previously enabled duplicates and dynamically discovered keys. Primary entities retain their IDs and settings. Removing additional entries can lose custom registry settings such as renamed entity IDs; do not rely on such customization surviving a mode toggle. Re-enabling developer mode uses the same unique IDs.

Developer mode restores previously registered Z-keys and enables integration-disabled sensors. Explicit user disabling is respected. On the tested HA version, user disabling was retained even across removal/recreation; this is not a guarantee that every custom registry attribute survives. Historical entities with a different unique-ID scheme are not automatically cleaned up.

## Earlier mapping and scale changes

The [sensor reference](sensors.md) defines current values. Earlier development revisions included different interpretations and a temporary neutral raw phase:

| Fields | Compatibility implication |
| --- | --- |
| z01 / z03 / z24 | Current values divide raw by 10; history from the neutral raw phase used ×1. z03/z24 have measurement metadata; z01 has kW/power/measurement. |
| z82 / z83 / z84 | Current values divide raw by 100 and display %. No statistics state class is set. |
| z00 / z121 | Current values use %/measurement. |
| z111 | Seconds in the main state, duration/measurement. |
| z158 | Current values divide raw by 10 and use kg/measurement; earlier revisions exposed raw integers or described a trip counter. |
| z96 | Historical RPM metadata was removed; developer mode exposes a unitless raw integer. |
| z10 / z41 | Added as operating state and phase time remaining with stable key-based IDs. |

Stable IDs do not make old and new statistics physically comparable. Review affected dashboards, automations, units and Statistics/Repairs before combining history. Changes to native English status text would also affect automation comparisons and require an explicit compatibility plan.

## Recorder and statistics

Registry cleanup, entry removal and metadata changes do not request deletion of Recorder history or statistics. No automatic rescaling, conversion, database edit or purge is performed. Normal retention and exclusions still apply.

Unknown developer fields have ordinary state history when Recorder includes them, but no assumed long-term statistics class. The z159 `total_increasing` contract is retained; lifetime scope and all physical reset rules have not been established by the short mapping capture. The z158 `measurement` contract permits decreases without interpreting them as counter resets.
