# Mapping evidence and compatibility

## Reviewed reference matches (19 November 2026)

A local review compared 40 paired EP20/cloud snapshots from one operating cycle
with the named reference values. The private capture and reproducible audit stay
in the gitignored local acceptance directory; identifiers and raw frames are not
published. Every mapping below matched its named reference in all 40 snapshots.
This establishes the reference association and conversion, not independent
physical calibration or validity for every controller configuration.

| Keys | Named reference | Divide raw by | Unit / statistics decision |
| --- | --- | --- | --- |
| z00 | Power | 1 | %/measurement; relative output interpretation adopted with user agreement |
| z01 | Power output | 10 | kW, power/measurement; user-confirmed implementation convention, supported by menu power range |
| z03 | Drop shaft | 10 | Temperature context supports °C; temperature/measurement |
| z24 | O2 wanted | 10 | Same oxygen scale as measured O2, including a manually recorded percent reading; %/measurement |
| z82, z83, z84 | O2 low/mid/high regulation | 100 | % as shown in the supplied web screenshot; no device or state class |
| z121 | Fan Speed | 1 | %/measurement; user-adopted unit |

Examples include z01=191 → 19.1, z03=356 → 35.6, z24=180 → 18,
and z82/z83/z84=24100/17000/20500 → 241/170/205. The latter are
regulation reference values, not oxygen concentration setpoints or verified
regulation thresholds. All eight primary fields above are enabled by default.

## Evidence continuity and adopted units

Historical tests and the historical mapping table remain evidence. A constant
value in a new capture does not refute an earlier dynamic test; lack of a unit
in one JSON object does not erase an earlier unit observation. New evidence
changes a mapping only where it adds a more specific association or exposes a
concrete conflict. The original historical observations remain in the linked
reference rather than being rewritten to match the newest capture.

The user adopts z01=kW, z18=%, z121=% and z123=Pa. z18 and z123 already use
those units, so their behavior is preserved. The historical table specifically
associates z18 with `frontdata.hopperdistance` in percent and z123 with pressure
in Pa. The new capture supports the named value associations; it does not
independently print these units. The user-adopted convention is recorded
separately from the 40/40 arithmetic matches.

z00 is implemented as relative power in percent. Additional support: menu
`auger.kw_min=3.8` and `auger.kw_max=28` accompany named Power 10%/100%
reference values. For the 17 running samples, interpolation
`3.8 + (z00 - 10) * (28 - 3.8) / 90` agrees with z01/10 to within 0.085 kW.
This supports a configured output percentage, not a claim of measured thermal
efficiency or electrical input power. The unit is an adopted interpretation;
raw cloud reference objects still do not explicitly carry a unit property.

## Main state, substate and timers

z10 is **Operating State**, with observed codes 2 = `Ignition 1`, 5 = `Running`
and 24 = `Stopped by external contact`. These follow the independently noted
operating events; transitions are bracketed by snapshots, not sampled at the
exact event second. Only these three codes are named. Unknown codes use
`Unknown (<number>)`; no unobserved stopped/alarm/ignition states are invented.
Status values use the existing English-text contract of the integration.

z40 retains the historical lookup unchanged, including its established code
2 and code 6 texts. Context of additional observed values is now documented:

| z40 | Observed z10 | Observed context | Lookup decision |
| --- | --- | --- | --- |
| 0 | 5 | Running, countdown zero | Keep numeric unknown until a direct substate label is available |
| 1 | 2 | Early ignition, countdown 14 s | No pellet/preheat label inferred |
| 4 | 2 | Timed ignition, countdown 281→230 s | Historical empty label retained as unknown |
| 6 | 24 | Cooling, countdown 535→20 s | Existing `Extinguish and cool` preserved |
| 224 | 24 | Stopped before ignition and after cooling | Possible no-substate marker in this context; the user reports a blank web substate |

z41 is **Phase Time Remaining**, raw seconds, duration/measurement, enabled by
default. It extends the historical cooling-countdown finding to the observed
ignition phases rather than discarding it. In z40=4, z41+z111=379 in both main
capture samples and in the earlier local session's sample (274+105). In cooling
z40=6, z41+z111=560 in all eleven samples. For the one z40=1 sample the sum is
60. These sums support phase deadlines relative to main-state entry; they are
not universal configured phase durations. The manual cooling display 9:30 is
approximate and does not establish a universal 570-second constant. Zero is
passed through as observed; it does not independently identify a phase ending.

z111 is **State Duration**, raw seconds, duration/measurement, enabled by
default. Across the observed stop/ignition/running/stop transitions its timer
resets with the main state. It continues when cooling ends while the main state
stays stopped (540 → 592 seconds). It is not complete combustion-cycle runtime.
Snapshot time minus timer differs from the manually noted transitions by about
5–7 seconds at the first samples; precise clock alignment remains unverified.

The cloud screens were requested sequentially after the TCP frame; individual
measurement timestamps were not saved. No `livedata_ref` reuse occurred in these
40 samples. The collector does not preserve TCP fragments reliably, so these
records are mapping evidence, not byte-faithful parser fixtures. See the
[tool limitations](../tools/README.md).

The [historical Z-value reference](NBE_zValue_maping.md) contains competing
hypotheses. The new dynamic named matches supersede its auger-counter,
return-temperature, oxygen-countdown and ignition-progress interpretations for
the fields above. Other historical mappings are not newly validated here.

## Remaining raw fields

z59 and z71 remain **unitless raw integers**, without device or state class.
They are excluded in normal mode and included in developer mode. For these
fields input 123 produces 123; missing and invalid values produce no value.

- z59/z71 matched z00/z24 in all 40 samples. They retain their raw contract
  and duplicate annotations; they do not automatically inherit the primary's
  scaling or unit. z59 is displayed as Power (z59). Their independent physical meaning remains unresolved.
- z96 previously used Fan RPM/rpm/measurement. Values 1046 → 20 → 1047 with
  Fan Speed references 33 → 32 → 35, and a resting value of 16, make the RPM
  interpretation unreliable. z96 has no fixed metadata entry and is excluded
  in normal mode. Developer mode discovers it as a unitless, unscaled raw
  integer without a statistics class when received, or restores it from an
  existing registry entry.

z158 is now mapped to Pellet Consumption 24h; see the
[adopted mapping](#adopted-z158-mapping-19-november-2026) below for evidence,
conversion and remaining limits.

Additional z40 labels are deferred. z101/z102 and other unknown fields remain
unresolved. z102=100 during cooling is already compatible with the historical
ignition/afterburning observation and is not treated as a refutation on its own.
Existing z25, z124 and z159 retain their historical behavior: constancy or a
small reference offset in a short new capture does not invalidate prior tests.
Their broader verification gaps remain documented in local acceptance evidence.
OP-07 remains open for unresolved units, meanings and reset rules.

## Local English language export review (19 November 2026)

OP-07 compared selected strings in the gitignored `docs/uk.json` with the
existing 40-snapshot session and the earlier two-snapshot session from the same
controller. The table distinguishes observed reference matches from candidate
field meanings. The stored cloud screens were read after the corresponding TCP
frame, so small value differences cannot establish rounding or sampling rules.

The suffix in `graphics_name_*` identifies a chart series slot. Slots 00–02
happen to match the Z suffixes. The confirmed associations 08 → z03, 06 → z04,
10 → z05 and 14 → z121 follow a different order with no common offset.
The export also groups heating zones in slots 44–59 and solar in 60–67.
For example, slot 59 labels a zone valve while z59 tracks power. The files
examined contain labels rather than a chart-slot-to-Z binding.

| Z-value | Previous mapping | Language key and text | Stored observation | Result |
| --- | --- | --- | --- | --- |
| z158 | Raw; historical trip hypothesis | `lng_hopper_3` “Consumption 24h”; `lng_hopper_5` “Trip 1”; `lng_hopper_13` “Trip 2” | ÷10 agrees exactly with 24h in 28/40 frames; differences are 11×+0.1 and 1×+0.2. Earlier frames show 0/1 raw against 0.0/0.0. Later reported web pair is 29 → 2.9 kg. Stored Trip 1 and Trip 2 are already 4441 and 9681 when z158 is zero. | **Adopted** as Pellet Consumption 24h, ÷10, kg, measurement; see the adopted mapping below. The saved Trip 1/2 displays do not match. Rolling window, calendar cutoff and other reset behavior remain open. |
| z159 | Total, kg ×1 | `lng_hopper_4` “Consumption total” | 16/40 exact, 24/40 one below the reference; both earlier frames match at 9591. | **Supported** total association and ×1 scale. The historical kg convention stands; the export gives no unit. Lifetime scope and reset behavior remain open. |
| z101 | Historical output-7 hypothesis | `setup_output_7` “L7” | z101+z158 is 228 in 38/40 main frames and both earlier frames, and 227 in two main frames. No paired named L7 reading in these sessions. | **Candidate** complementary quantity in raw counts. The sum alone cannot assign physical meaning, kg, ÷10, or a reset rule. |
| z00 / z01 | Relative power / power output | `graphics_name_00` “Power (%)”; `graphics_name_01` “Power (kW)” | Each 40/40 with ×1 / ÷10; z01=191 → 19.1. | **Confirmed** reference associations and scales. Chart units support the adopted % / kW conventions. |
| z02 / z03 / z04 / z05 | Boiler / shaft / flue gas / O₂ | `graphics_name_02` “Boiler  (°C)”; `graphics_name_08` “Shaft (°C)”; `graphics_name_06` “Smoke (°C)”; `graphics_name_10` “O2 (%)” | Each 40/40 after ÷10 against its named reference. | **Confirmed** reference associations and scales; chart units agree. |
| z24 / z25 | O₂ setpoint / boiler setpoint | `graphics_name_11` “Wanted O2 (%)”; `graphics_name_03` “Wanted boiler (°C)” | z24 ÷10 matches 40/40; z25 stays 700 against 70 in the reference and menu. | **Confirmed** for z24; **supported** for z25 by a constant and its configuration reference. |
| z18 / z121 / z123 | Hopper % / fan % / combustion pressure Pa | `graphics_name_21` “Hopper content (%)”; `graphics_name_14` “Fan speed (%)”; `graphics_name_17` “Boiler vacuum (Pa)” | Each 40/40 at ×1 against hopper reference #42, Fan Speed and Pressure. The other Hopper content reference (#16) is negative and differs from z18. | **Confirmed** reference associations and scales; chart labels support adopted units. |
| z115 | Historical ash level | `graphics_name_16` “ Ash box (%)” | z115 and unnamed reference #39 are both 53 in all 42 frames. Historical mapping cites `frontdata.ashdist`. | **Plausible** ash level in % at ×1. The new comparison is constant and the stored reference label is blank. |
| z54 / z55 / z57 | Historical auger timing hypotheses | `lng_hopper_11` “Actual auger time”; `lng_hopper_12` “Actual auger pause” | During Running raw values are 39–44 / 10 / 10–12; all are zero outside Running in the saved sessions. Neither named timing series is saved. | **Candidates** for timing; individual assignment, divisor and unit open. |
| z102 | Historical igniter output | `lng_output_igniter` “Igniter” | 100 during ignition and cooling; 77/49/24 then 10 while Running, 0 at rest. No named output series in the snapshots. | **Open**. The label identifies an available output, with no field binding or unit evidence. |
| z163 | Historical return-temperature candidate | `graphics_name_07` “Return (°C)” | Raw 222–227 across both sessions would give 22.2–22.7 °C at ÷10. No independently named return reading. | **Open**. Range alone supports testing the hypothesis but cannot establish field, scale or unit. |
| z10 | Main operating state | `lng_state_2` “Ignition 1”; `lng_state_5` “Running”; `lng_state_24` “Stopped by external contact” | Same-frame pairs below follow the recorded ignition, running, cooling and stopped sequence. | **Confirmed** export texts for the three observed codes. |
| z40 | Substate code | `lng_substate_0` `""`; `lng_substate_1` “Ignition ventilating”; `lng_substate_4` “Ignition”; `lng_substate_6` “Extinguish the fire and cooling burner”; `lng_substate_224` `" "` | Same-frame pairs below. The reported web substate for 224 is blank. | **Confirmed** export entries for the observed codes. Code 0 is an empty string and 224 is one space. The export adds explicit text for 1 and 4 in the observed ignition context. |

Same-frame counts use the original snapshot `zvals` for both fields.

| (z10, z40) | Main session | Earlier session | Observed context |
| --- | ---: | ---: | --- |
| (2, 1) | 1 | 0 | Early ignition, z41=14 s |
| (2, 4) | 2 | 1 | Timed ignition, z41=281/230 s and 274 s earlier |
| (5, 0) | 17 | 0 | Running, z41=0 |
| (24, 6) | 11 | 0 | Cooling while externally stopped, z41=535→20 s |
| (24, 224) | 9 | 1 | Stopped, blank web substate as reported |

### Numeric key cross-check

An exact numeric-token search of JSON keys found no family with matching
same-number labels for z03, z04 and z05. The boiler display family provides
three exact matches to the saved reference names, in a different order:

| Z-value | Saved reference, ÷10 | Boiler display label | Same-number boiler key |
| --- | --- | --- | --- |
| z03 | Drop shaft, 40/40 | `lng_boil_7` “Drop shaft” | `lng_boil_3` “Chimney/smoke” |
| z04 | Chimney/smoke, 40/40 | `lng_boil_3` “Chimney/smoke” | `lng_boil_4` “Power” |
| z05 | O2, 40/40 | `lng_boil_12` “O2” | `lng_boil_5` “Power output” |

For 121, 123 and 158 the only shared numeric family was `lng_setup_*` and
its tooltip variants. The labels are “Correction at 50% power”, an empty
string and an empty string, respectively. The saved display names instead
match `lng_boil_25` “Fan Speed”, `lng_boil_24` “Pressure” and, for the
z158 mapping, `lng_hopper_3` “Consumption 24h”. These matches identify
display labels. The export links neither those keys nor the chart keys
directly to UART fields.

The same-frame counts establish the combinations in the saved cycle. Other
combinations remain untested. The export also has `lng_substate_2` “Ignition
preheat”, `lng_substate_3` “Ignition pellets” and `lng_substate_5` `""`; those
codes did not occur in either session. The text for code 3 differs from the
historical empty entry. The text for code 4 updates the historical evidence
above, where it was treated as empty. The language-export review itself did
not change enum or sensor metadata; the later adopted z158 mapping is below.

## Existing installations and statistics

The unique ID stays `<config-entry-id>_<z-key>`. The current metadata table
contains 26 named sensors: normal mode creates the 21 primary sensors and
excludes the five duplicates (z50, z60, z59, z70 and z71). Developer mode
includes all 26 named sensors and discovers additional numeric Z-keys from
received measurements, so its final sensor count depends on the stream.

Developer mode restores previously registered Z-keys and enables sensors
disabled by the integration; explicit user disabling is respected. Normal mode
removes additional Z-value entities from the registry, including previously
enabled duplicates and z96. Switching developer mode off therefore loses
custom registry settings for those additional entities. Re-enabling it recreates
them with the same unique IDs. Retained primary entities keep their IDs and
registry settings. z10 and z41 were added with stable unique IDs.

Registry cleanup does not request deletion of recorder history or statistics;
normal Recorder retention still applies, including to existing z96 history.

This update changes future values of z01/z03/z24 (divide by 10) and z82/z83/z84
(divide by 100) relative to their neutral raw phase. z03/z24 regain units and
measurement state classes; z111 gains seconds/duration/measurement. With the
user-adopted units z00/z01/z121 now use measurement; z01 also uses power device
class. z82–z84 display % and retain no statistics state class.
Existing statistics may describe an earlier physical interpretation, the
neutral raw phase, or both, depending on installed
revisions. Stable entity IDs do not make those series comparable.

Review affected dashboards, automations, names, units and Statistics/Repairs
before combining history. No automatic history conversion, deletion or database
edit occurs. Removing speculative metadata does not remove old statistics;
restoring a scale does not rescale stored raw history.

This is not a production release or a claim of actual Home Assistant UI or
recorder compatibility testing. Local tests exercise real entity conversion
through framework doubles, including invalid/missing data and stable IDs.

## Adopted z158 mapping (19 November 2026)

The user adopted z158 as Pellet Consumption 24h: divide raw by 10, kg,
measurement, enabled by default. Raw 29 becomes 2.9 kg. Measurement permits
decreases without treating them as counter resets. This replaces the historical
raw/unscaled interpretation of z158.

Evidence: 28/40 exact named Consumption 24h matches, eleven differences of
0.1 and one of 0.2; a later user-observed pair was raw 29 and web 2.9 kg.
The exact time window and reset rules remain unverified. The unique ID is
unchanged. Explicit user disabling is respected; developer mode enables
integration-disabled sensors as described above. Old raw history is not
converted. No live access or deployment was performed for that mapping change.

Offline verification recorded for the z158 change: entity/diagnostic suite
10/10 and parser suite 23/23
passed with Python 3.12.14. The new conversion test failed first (29 vs 2.9)
and passed after the metadata change. Tests remain in local acceptance files.
