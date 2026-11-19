# Sensor reference

This is the current implemented sensor contract. The [mapping evidence](mapping-evidence.md) separately records what is established, what remains uncertain and what cannot be inferred from this installation. Implementation alone does not prove a physical meaning.

## Normal mode

Normal mode creates 21 primary sensors from the central metadata in `const.py`. A conversion of ÷10 means the integer received in the frame is divided by 10.

| Z-key | Sensor | Conversion | Unit | State class |
| --- | --- | --- | --- | --- |
| z00 | Power | ×1 | % | measurement |
| z01 | Power output | ÷10 | kW | measurement |
| z02 | Boiler temperature | ÷10 | °C | measurement |
| z03 | Drop shaft temperature | ÷10 | °C | measurement |
| z04 | Flue gas temperature | ÷10 | °C | measurement |
| z05 | Oxygen | ÷10 | % | measurement |
| z10 | Operating state | Lookup, otherwise `Unknown (<number>)` | — | — |
| z18 | Hopper content | ×1 | % | measurement |
| z24 | Oxygen setpoint | ÷10 | % | measurement |
| z25 | Boiler setpoint | ÷10 | °C | measurement |
| z40 | Substate | Lookup, otherwise `Unknown (<number>)` | — | — |
| z41 | Phase time remaining | ×1 | s | measurement |
| z82 | Oxygen low regulation | ÷100 | % | — |
| z83 | Oxygen mid regulation | ÷100 | % | — |
| z84 | Oxygen high regulation | ÷100 | % | — |
| z111 | State duration | ×1 | s | measurement |
| z121 | Fan speed | ×1 | % | measurement |
| z123 | Combustion chamber pressure | ×1 | Pa | measurement |
| z124 | Outdoor temperature | ÷10 | °C | measurement |
| z158 | Pellet consumption last 24 hours | ÷10 | kg | measurement |
| z159 | Total consumption | ×1 | kg | total_increasing |

The O2 regulation fields are reference values, not oxygen concentration setpoints; their controller semantics remain open. The z158 value may decrease, so it is not treated as a monotonically increasing counter. The exact 24-hour window and reset behavior remain unverified.

## Additional developer sensors

The metadata contains five more named fields, for 26 named sensors in total. These are excluded in normal mode and included in developer mode:

| Z-key | Display meaning | Conversion | Unit | State class |
| --- | --- | --- | --- | --- |
| z50 / z60 | Boiler temperature duplicates of z02 | ÷10 | °C | measurement |
| z59 | Power (z59), observed equal to z00 | ×1 | — | — |
| z70 | Oxygen duplicate of z05 | ÷10 | % | measurement |
| z71 | Unverified raw field, observed equal to z24 | ×1 | — | — |

Additional received numeric keys, including z96, are discovered as raw integers. They do not inherit a guessed scale, unit or statistics class. The developer sensor count depends on received and previously registered keys. Configuration and registry behavior are described in [configuration](configuration.md#developer-mode) and [compatibility](compatibility.md).

## State text

Main state z10 currently names observed codes 2 = `Ignition 1`, 5 = `Running`, and 24 = `Stopped by external contact`. Unknown codes retain their numeric code in the text.

z40 retains the existing substate lookup for compatibility. For example, 2 gives `Ignition preheat` and 6 gives `Extinguish and cool`. Other existing lookup labels are historical; they have not all been observed in the reviewed cycle. Codes without an implemented label, including 0, 1, 4 and 224, use `Unknown (<number>)`. The [language-export evidence](mapping-evidence.md#state-and-timer-evidence) records additional labels without silently changing automation-facing values.

Names are provided in German and English; native state texts remain English. Missing or invalid values yield no sensor value. Values that overflow a scaled numeric conversion are ignored; a subsequent valid value can recover normally.
