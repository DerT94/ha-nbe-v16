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
| z82, z83, z84 | O2 low/mid/high regulation | 100 | Regulator units unresolved; no unit or device/state class |
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
| 224 | 24 | Stopped before ignition and after cooling | No universal standby label inferred |

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

z59, z71, z96 and z158 remain **unitless raw integers, disabled by default**,
without device or state class. For these fields input 123 produces 123;
missing and invalid values produce no value. Existing keys and unique IDs remain.

- z59/z71 matched z00/z24 in all 40 samples. They retain their raw contract
  and duplicate annotations; they do not automatically inherit the primary's
  scaling or unit. Their independent physical meaning remains unresolved.
- z96 previously used Fan RPM/rpm/measurement. Values 1046 → 20 → 1047 with
  Fan Speed references 33 → 32 → 35, and a resting value of 16, make the RPM
  interpretation unreliable. The field is now neutral raw data; a bitmask is
  a hypothesis, not a confirmed replacement meaning.
- z158 divided by 10 matched Consumption 24h in 28/40 samples; eleven differed
  by +0.1 and one by +0.2. No reset was captured. Neither a 24-hour nor trip
  interpretation or counter state class is enabled.

Additional z40 labels are deferred. z101/z102 and other unknown fields remain
unresolved. z102=100 during cooling is already compatible with the historical
ignition/afterburning observation and is not treated as a refutation on its own.
Existing z25, z124 and z159 retain their historical behavior: constancy or a
small reference offset in a short new capture does not invalidate prior tests.
Their broader verification gaps remain documented in local acceptance evidence.
OP-07 remains open for unresolved units, meanings and reset rules.

## Existing installations and statistics

The unique ID stays `<config-entry-id>_<z-key>`. No entities or recorder history
are deleted. Registry choices and existing user names persist: changing a default
does not automatically enable a restored field or disable z96 in an installation.
New installations have 27 sensors, 20 enabled and 7 disabled by default.
z10 and z41 add new keys; all 25 previous keys and unique IDs are retained.

This update changes future values of z01/z03/z24 (divide by 10) and z82/z83/z84
(divide by 100) relative to their neutral raw phase. z03/z24 regain units and
measurement state classes; z111 gains seconds/duration/measurement. With the
user-adopted units z00/z01/z121 now use measurement; z01 also uses power device
class. z82–z84 retain no statistics state class while units remain unresolved.
z96 loses rpm and measurement. Existing statistics may describe an earlier
physical interpretation, the neutral raw phase, or both, depending on installed
revisions. Stable entity IDs do not make those series comparable.

Review affected dashboards, automations, names, units and Statistics/Repairs
before combining history. No automatic history conversion, deletion or database
edit occurs. Removing speculative metadata does not remove old statistics;
restoring a scale does not rescale stored raw history.

This is not a production release or a claim of actual Home Assistant UI or
recorder compatibility testing. Local tests exercise real entity conversion
through framework doubles, including invalid/missing data and stable IDs.
