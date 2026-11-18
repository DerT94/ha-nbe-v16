# Mapping evidence and compatibility

The historical [Z-value reference](NBE_zValue_maping.md) records snapshot
correlations, including hypotheses. Its underlying paired snapshots are not
present in this checkout. The historical collector also does not preserve TCP
line fragments reliably; see [the tool limitations](../tools/README.md).
Neither that document nor a correctly parsed numeric value independently proves
every physical meaning or unit.

## Disputed fields

These fields are exposed as **unitless raw integers, disabled by default**.
They have no device class or state class and do not create new long-term
statistics. This is an explicit unknown mapping, not a newly inferred physical
measurement. The existing keys and entity unique IDs are retained.

| Keys | Earlier interpretation | Contradicting or missing evidence in the reference |
| --- | --- | --- |
| z00, z59 | Power in percent | z00 may instead be an auger counter; equality with z59 does not establish a unit. |
| z01 | Power output in kW, divided by 10 | The reference suggests a cumulative auger counter. |
| z03 | Drop shaft temperature | The reference suggests return temperature. |
| z24, z71 | Oxygen setpoint, divided by 10 | Reported countdown behavior and matching values do not establish an oxygen unit. |
| z82, z83, z84 | Oxygen regulation thresholds, divided by 100 | The reference lists constant, unresolved values 7700/14800/17800. |
| z121 | Fan speed in percent | The reference suggests ignition progress and explicitly leaves the field unresolved. |
| z111 | Complete combustion-cycle runtime in seconds | The reference describes time in the current state; the paired state transitions are unavailable for independent verification. |
| z158 | Consumption over 24 hours, divided by 10 | The reference describes trip consumption with uncertain reset behavior; the underlying paired evidence is unavailable. |

For each raw field, an input integer such as `123` must produce `123`, with no
unit or inferred conversion. Missing and non-integer values produce no value.
Offline synthetic tests can verify this contract independently of the metadata;
they cannot establish a physical interpretation.

Other existing mappings retain their current behavior during this correction.
This does not elevate historical correlations to a fresh independent validation.
Confirming disputed mappings requires a sanitized, byte-faithful operational
frame paired with an independently named reference value/unit and, where
relevant, observations across resets or operating-state changes.

## Existing installations and statistics

The unique ID remains `<config-entry-id>_<z-key>` for every sensor. Updating the
integration does not delete entities or recorder history. Home Assistant keeps
existing registry choices, so changing the default does **not** automatically
disable an already enabled sensor. Review existing disputed entities and any
automations or dashboards that use their former names or scaled values.

Removing the speculative unit, scaling and state class changes the meaning of
future readings from disputed entities. Existing long-term statistics still
refer to the previous interpretation and must not be treated as comparable raw
measurements. No automatic history conversion, deletion, or recorder/database
edit is performed. Review Statistics/Repairs in Home Assistant before combining
old history with later confirmed units. The integration does not silently
rewrite a historical percent/kW/temperature/consumption series into raw units.

This correction is not a production release or a claim that compatibility has
been tested on an actual Home Assistant target version.
